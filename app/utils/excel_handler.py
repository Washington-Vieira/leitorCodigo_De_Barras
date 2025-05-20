import pandas as pd
from datetime import datetime
import os
from tkinter.filedialog import asksaveasfilename
from ..config import DATA_DIR, RELATORIOS_DIR
import sqlite3
from ..models.database import Database

class ExcelHandler:
    def __init__(self):
        self.PASTA_EXCEL = 'data/excel_importados'
        self.PASTA_RELATORIOS = RELATORIOS_DIR

    def exportar_para_excel(self, tree, nome_arquivo_default):
        data_hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nome_sugerido = f"{nome_arquivo_default.split('.')[0]}_{data_hora_atual}.xlsx"
        
        # Permitir que o usuário escolha onde salvar
        caminho_completo = asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
            initialfile=nome_sugerido,
            title="Salvar relatório como"
        )
        
        if not caminho_completo:  # Se o usuário cancelou a operação
            return

        colunas = [tree.heading(col)["text"] for col in tree["columns"]]
        dados = [tree.item(item, "values") for item in tree.get_children()]

        df = pd.DataFrame(dados, columns=colunas)
        df.to_excel(caminho_completo, index=False, engine="openpyxl")
        print(f"✅ Relatório salvo em: {caminho_completo}")

    def exportar_relatorio_controladoria(self, data_selecionada=None):
        """Exporta relatório consolidado para a controladoria no formato específico"""
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(Database.DB_NAME)
            
            # Preparar a consulta SQL base
            query = """
            SELECT 
                p.item as Material,
                SUM(p.quantidade) as Quantidade
            FROM leituras l
            JOIN produtos p ON l.serial = p.serial
            """
            
            # Adicionar filtro de data se fornecida
            if data_selecionada:
                # Converter a data para o formato do banco (YYYY-MM-DD)
                data_str = data_selecionada.strftime('%Y-%m-%d')
                query += f" WHERE l.data_leitura LIKE '{data_str}%'"
            
            # Agrupar e ordenar
            query += """
            GROUP BY p.item
            ORDER BY p.item
            """
            
            # Criar DataFrame com os resultados
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Verificar se há dados
            if df.empty:
                print(f"⚠️ Nenhum dado encontrado para a data {data_selecionada.strftime('%d/%m/%Y')}")
                return False
            
            # Criar as colunas fixas na ordem exata solicitada
            df.insert(0, 'Txt.cab.doc.', '')  # Coluna vazia
            df.insert(1, 'Tipo de Movimento', 'Z41')
            df.insert(3, 'Centro De', '6112')
            df.insert(4, 'Depósito De', 'SB01')
            df.insert(5, 'Centro Para', '6112')
            df.insert(6, 'Depósito Para', 'SB01')
            df.insert(7, 'Ordem Cliente De', '')
            df.insert(8, 'Item da Ordem Cliente De', '')
            df.insert(9, 'Ordem Cliente Para', '')
            df.insert(10, 'Item da Ordem Cliente Para', '')
            df.insert(12, 'Fornecedor', 'BP6118')
            df.insert(13, 'IVA', 'K1')
            
            # Solicitar local para salvar
            data_str_nome = data_selecionada.strftime("%d_%m_%Y") if data_selecionada else datetime.now().strftime("%d_%m_%Y")
            nome_sugerido = f"Relatorio_Controladoria_{data_str_nome}.xlsx"
            
            caminho_completo = asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
                initialfile=nome_sugerido,
                title="Salvar relatório de controladoria como"
            )
            
            if not caminho_completo:  # Se o usuário cancelou a operação
                return False
            
            # Criar um escritor Excel
            writer = pd.ExcelWriter(caminho_completo, engine='openpyxl')
            
            # Escrever o DataFrame
            df.to_excel(writer, sheet_name='Planilha1', index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Planilha1']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = max_length
            
            # Salvar o arquivo
            writer.close()
            
            print(f"✅ Relatório de controladoria salvo em: {caminho_completo}")
            if data_selecionada:
                print(f"📅 Data do relatório: {data_selecionada.strftime('%d/%m/%Y')}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório de controladoria: {e}")
            return False

    def exportar_relatorio_caixas(self, dados, incluir_detalhes=True):
        """
        Exporta um relatório das caixas fechadas para Excel
        
        Args:
            dados: Lista de dicionários com dados das caixas
            incluir_detalhes: Se True, inclui uma aba com detalhes dos itens de cada caixa
        """
        import pandas as pd
        from datetime import datetime
        import sqlite3
        from tkinter import filedialog
        from app.models.database import Database
        
        # Criar DataFrame principal com as caixas
        df_caixas = pd.DataFrame(dados)
        
        # Solicitar local para salvar
        data_atual = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        nome_arquivo = f"relatorio_caixas_{data_atual}.xlsx"
        
        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=nome_arquivo,
            filetypes=[("Arquivos Excel", "*.xlsx")]
        )
        
        if caminho:
            # Criar um writer do Excel para múltiplas abas
            with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
                # Exportar resumo das caixas
                df_caixas.to_excel(writer, index=False, sheet_name="Resumo Caixas")
                
                if incluir_detalhes:
                    # Conectar ao banco para buscar detalhes dos itens
                    conn = sqlite3.connect(Database.DB_NAME)
                    
                    # Buscar detalhes de todos os itens das caixas
                    query = """
                    SELECT 
                        l.numero_caixa,
                        l.serial,
                        l.pedido_lido,
                        p.item,
                        p.maquina,
                        l.linha_lida,
                        p.quantidade as qtd_programada,
                        (
                            SELECT SUM(pp.quantidade)
                            FROM produtos pp
                            WHERE pp.serial = l.serial
                        ) as qtd_enviada,
                        l.data_leitura,
                        l.hora_leitura,
                        c.data_fechamento,
                        c.hora_fechamento,
                        c.usuario_fechamento
                    FROM leituras l
                    LEFT JOIN produtos p ON l.serial = p.serial
                    LEFT JOIN caixas c ON l.numero_caixa = c.numero_caixa
                    WHERE l.numero_caixa IN (
                        SELECT DISTINCT numero_caixa 
                        FROM caixas 
                        WHERE status = 'FECHADA'
                    )
                    ORDER BY 
                        l.numero_caixa,
                        l.data_leitura,
                        l.hora_leitura
                    """
                    
                    # Criar DataFrame com detalhes
                    df_detalhes = pd.read_sql_query(query, conn)
                    
                    # Formatar datas para dd/mm/yyyy
                    for col in ['data_leitura', 'data_fechamento']:
                        df_detalhes[col] = pd.to_datetime(df_detalhes[col]).dt.strftime('%d/%m/%Y')
                    
                    # Exportar detalhes em uma nova aba
                    df_detalhes.to_excel(writer, index=False, sheet_name="Detalhes Itens")
                    
                    # Ajustar largura das colunas
                    for sheet in writer.sheets.values():
                        for idx, col in enumerate(sheet.columns):
                            max_length = 0
                            for cell in col:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = (max_length + 2)
                            sheet.column_dimensions[chr(65 + idx)].width = adjusted_width
                    
                    conn.close()
            
            return True
        
        return False

    def exportar_relatorio_caixas_por_data(self, data_inicio, data_fim):
        """
        Exporta relatório de caixas fechadas filtrado por período
        
        Args:
            data_inicio: Data inicial no formato datetime
            data_fim: Data final no formato datetime
        """
        import sqlite3
        from app.models.database import Database
        import pandas as pd
        from datetime import datetime
        from tkinter import filedialog
        
        # Conectar ao banco
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        # Buscar caixas no período
        query_caixas = """
        SELECT 
            c.numero_caixa,
            c.total_itens,
            c.data_fechamento,
            c.hora_fechamento,
            COALESCE(c.usuario_fechamento, 'Sistema') as usuario_fechamento,
            COUNT(l.serial) as total_leituras
        FROM caixas c
        LEFT JOIN leituras l ON c.numero_caixa = l.numero_caixa
        WHERE c.status = 'FECHADA'
        AND c.data_fechamento BETWEEN ? AND ?
        GROUP BY 
            c.numero_caixa, c.total_itens, c.data_fechamento, 
            c.hora_fechamento, c.usuario_fechamento
        ORDER BY c.data_fechamento DESC, c.hora_fechamento DESC
        """
        
        # Buscar detalhes dos itens
        query_itens = """
        SELECT 
            l.numero_caixa,
            l.pedido_lido as Pedido,
            p.data_pedido as 'Data do Pedido',
            l.serial as Serial,
            p.item as Item,
            p.maquina as Máquina,
            l.linha_lida as Linha,
            p.quantidade as 'Qtd Programada',
            (
                SELECT SUM(pp.quantidade)
                FROM produtos pp
                WHERE pp.serial = l.serial
            ) as 'Qtd Enviada',
            p.nome_status as Status,
            l.data_leitura as 'Data Leitura',
            l.hora_leitura as 'Hora Leitura',
            CASE 
                WHEN p.data_pedido IS NULL THEN NULL
                ELSE CAST(
                    JULIANDAY(l.data_leitura) - JULIANDAY(
                        substr(p.data_pedido, 7, 4) || '-' || 
                        substr(p.data_pedido, 4, 2) || '-' || 
                        substr(p.data_pedido, 1, 2)
                    ) AS INTEGER
                )
            END as 'Diferença em Dias'
        FROM leituras l
        LEFT JOIN produtos p ON l.serial = p.serial
        LEFT JOIN caixas c ON l.numero_caixa = c.numero_caixa
        WHERE c.status = 'FECHADA'
        AND c.data_fechamento BETWEEN ? AND ?
        ORDER BY 
            l.numero_caixa,
            l.data_leitura,
            l.hora_leitura
        """
        
        # Executar queries
        cursor.execute(query_caixas, (
            data_inicio.strftime('%Y-%m-%d'),
            data_fim.strftime('%Y-%m-%d')
        ))
        caixas_data = cursor.fetchall()
        
        cursor.execute(query_itens, (
            data_inicio.strftime('%Y-%m-%d'),
            data_fim.strftime('%Y-%m-%d')
        ))
        itens_data = cursor.fetchall()
        
        if not caixas_data:
            conn.close()
            return False
            
        # Criar DataFrames
        df_caixas = pd.DataFrame(caixas_data, columns=[
            'Número da Caixa',
            'Total de Itens',
            'Data de Fechamento',
            'Hora de Fechamento',
            'Fechado por',
            'Total de Leituras'
        ])
        
        df_itens = pd.DataFrame(itens_data, columns=[
            'Número da Caixa',
            'Pedido',
            'Data do Pedido',
            'Serial',
            'Item',
            'Máquina',
            'Linha',
            'Qtd Programada',
            'Qtd Enviada',
            'Status',
            'Data Leitura',
            'Hora Leitura',
            'Diferença em Dias'
        ])
        
        # Formatar datas
        df_caixas['Data de Fechamento'] = pd.to_datetime(df_caixas['Data de Fechamento']).dt.strftime('%d/%m/%Y')
        
        # Tratar valores nulos na data do pedido
        df_itens['Data do Pedido'] = df_itens['Data do Pedido'].fillna('')
        
        # Formatar data de leitura para dd/mm/yyyy
        df_itens['Data Leitura'] = pd.to_datetime(df_itens['Data Leitura']).dt.strftime('%d/%m/%Y')
        
        # Formatar diferença em dias
        df_itens['Diferença em Dias'] = df_itens['Diferença em Dias'].fillna('-')
        df_itens.loc[df_itens['Diferença em Dias'] != '-', 'Diferença em Dias'] = \
            df_itens.loc[df_itens['Diferença em Dias'] != '-', 'Diferença em Dias'].astype(int)
        
        # Solicitar local para salvar
        periodo = f"{data_inicio.strftime('%d-%m-%Y')}_a_{data_fim.strftime('%d-%m-%Y')}"
        nome_arquivo = f"relatorio_caixas_{periodo}.xlsx"
        
        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=nome_arquivo,
            filetypes=[("Arquivos Excel", "*.xlsx")]
        )
        
        if caminho:
            # Criar um writer do Excel para múltiplas abas
            with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
                # Exportar resumo das caixas
                df_caixas.to_excel(writer, index=False, sheet_name="Resumo Caixas")
                
                # Exportar detalhes dos itens
                df_itens.to_excel(writer, index=False, sheet_name="Detalhes Itens")
                
                # Ajustar largura das colunas em ambas as abas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    df = df_caixas if sheet_name == "Resumo Caixas" else df_itens
                    
                    for idx, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(str(col))
                        ) + 2
                        worksheet.column_dimensions[chr(65 + idx)].width = max_length
            
            conn.close()
            return True
        
        conn.close()
        return False