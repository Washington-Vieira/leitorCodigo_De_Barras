import os
import pandas as pd
import unicodedata
from datetime import datetime
from ..models.database import Database
from ..models.produto import Produto
from ..config import RELATORIOS_DIR
import sqlite3
import time

class ExcelImporter:
    def __init__(self):
        self.PASTA_EXCEL = 'data/excel_importados'
        self.status_callback = None
        
    def set_callback(self, callback):
        """Define o callback para notificar mudanças de status"""
        self.status_callback = callback
        
    def normalizar_coluna(self, col):
        col = col.strip().replace('\xa0', ' ')
        col = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode()
        return col

    def _salvar_log(self, nome_arquivo, stats):
        """Salva o log de importação em um arquivo"""
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nome_log = f"log_importacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        caminho_log = os.path.join(RELATORIOS_DIR, nome_log)
        
        with open(caminho_log, 'w', encoding='utf-8') as f:
            f.write(f"📊 RELATÓRIO DE IMPORTAÇÃO - {nome_arquivo}\n")
            f.write(f"Data/Hora: {data_hora}\n")
            f.write("="*50 + "\n\n")
            f.write("RESUMO:\n")
            f.write(f"➕ Registros inseridos: {stats['inseridos']}\n")
            f.write(f"⏭️ Registros ignorados: {stats['ignorados']}\n")
        
        print(f"📝 Log de importação salvo em: {caminho_log}")

    def _processar_arquivo(self, arquivo):
        stats = {'inseridos': 0, 'atualizados': 0, 'ignorados': 0, 'identificados': 0}
        
        try:
            # Tentar abrir o arquivo com um bloco try/except específico
            try:
                df = pd.read_excel(os.path.join(self.PASTA_EXCEL, arquivo))
            except PermissionError:
                print(f"⚠️ O arquivo {arquivo} está sendo usado por outro programa.")
                print("Por favor, feche o arquivo e tente novamente.")
                return None
            except Exception as e:
                print(f"❌ Erro ao abrir o arquivo {arquivo}: {str(e)}")
                return None
                
            df.columns = [self.normalizar_coluna(col) for col in df.columns]
            
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    serial = str(row.get('Serial', '')).strip()
                    maquina = str(row.get('Maquina', '')).strip()
                    
                    if not serial or not maquina:
                        continue
                        
                    cursor.execute("SELECT nome_status FROM produtos WHERE serial = ? AND maquina = ?", 
                                 (serial, maquina))
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        nome_status_existente = resultado[0]
                        nome_status_novo = str(row.get('Nome Status', '')).strip()
                        
                        if nome_status_existente != nome_status_novo:
                            cursor.execute('''
                                UPDATE produtos SET
                                    pedido = ?, data_pedido = ?, linha_mae = ?, area = ?, 
                                    linha_ato = ?, item = ?, quantidade = ?, 
                                    nome_status = ?, data_producao = ?
                                WHERE serial = ? AND maquina = ?
                            ''', (
                                str(row.get('Pedido', '')).strip(),
                                str(row.get('Data Pedido', '')).strip(),
                                str(row.get('Linha MAE', '')).strip(),
                                str(row.get('Area', '')).strip(),
                                str(row.get('Linha ATO', '')).strip(),
                                str(row.get('Item', '')).strip(),
                                int(row.get('Quantidade', 0)),
                                nome_status_novo,
                                str(row.get('Data Producao', '')).strip(),
                                serial,
                                maquina
                            ))
                            stats['atualizados'] += 1
                            
                            if self.status_callback:
                                self.status_callback(serial, nome_status_novo)
                        else:
                            stats['ignorados'] += 1
                    else:
                        try:
                            cursor.execute('''
                                INSERT INTO produtos (
                                    pedido, data_pedido, linha_mae, area, maquina,
                                    linha_ato, item, serial, quantidade, nome_status, data_producao
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                str(row.get('Pedido', '')).strip(),
                                str(row.get('Data Pedido', '')).strip(),
                                str(row.get('Linha MAE', '')).strip(),
                                str(row.get('Area', '')).strip(),
                                maquina,
                                str(row.get('Linha ATO', '')).strip(),
                                str(row.get('Item', '')).strip(),
                                serial,
                                int(row.get('Quantidade', 0)),
                                str(row.get('Nome Status', '')).strip(),
                                str(row.get('Data Producao', '')).strip()
                            ))
                            stats['inseridos'] += 1
                            
                            # Verificar se este serial estava nos códigos não identificados
                            cursor.execute('''
                                SELECT id, status FROM codigos_nao_identificados 
                                WHERE serial = ?
                            ''', (serial,))
                            codigo_nao_identificado = cursor.fetchone()
                            
                            if codigo_nao_identificado:
                                # Atualizar o status do código não identificado
                                cursor.execute('''
                                    UPDATE codigos_nao_identificados
                                    SET status = 'IDENTIFICADO',
                                        data_identificacao = ?,
                                        hora_identificacao = ?,
                                        observacao = ?
                                    WHERE id = ?
                                ''', (
                                    datetime.now().strftime('%Y-%m-%d'),
                                    datetime.now().strftime('%H:%M:%S'),
                                    "Identificado automaticamente durante importação de planilha",
                                    codigo_nao_identificado[0]
                                ))
                                stats['identificados'] += 1
                                
                                # Notificar a interface sobre o código identificado
                                if self.status_callback:
                                    # Notificar a interface imediatamente
                                    self.status_callback(serial, "CODIGO_IDENTIFICADO")
                                    print(f"✨ Código {serial} identificado e notificado para a interface")
                                
                        except sqlite3.IntegrityError:
                            stats['ignorados'] += 1
                            
                except Exception as e:
                    continue
                    
            conn.commit()
            conn.close()
            
            # Salvar log de importação
            self._salvar_log(arquivo, stats)
            
            print(f"\n📊 Resumo da importação de {arquivo}:")
            print(f"   ➕ Inseridos   : {stats['inseridos']} novos registros")
            print(f"   ⏭️ Ignorados  : {stats['ignorados']} (sem alterações necessárias)")
            print(f"   ✅ Códigos não identificados processados: {stats['identificados']}")
            
            if stats['identificados'] > 0:
                print("\n🎯 Detalhes dos códigos identificados:")
                print("   - Os códigos foram automaticamente movidos para 'Identificados'")
                print("   - A data e hora de identificação foram registradas")
                print("   - As interfaces foram atualizadas automaticamente")
            
            print("\n📝 Um relatório detalhado foi salvo em data/relatorios")
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo {arquivo}: {e}")
            return None
            
        return stats

    def importar_excels(self):
        if not os.path.exists(self.PASTA_EXCEL):
            os.makedirs(self.PASTA_EXCEL)
            print(f"⚠️ Pasta '{self.PASTA_EXCEL}' criada. Coloque os arquivos Excel lá e execute novamente.")
            return

        arquivos = [f for f in os.listdir(self.PASTA_EXCEL) if f.endswith(('.xlsx', '.xls'))]
        if not arquivos:
            print(f"⚠️ Nenhum arquivo Excel encontrado na pasta '{self.PASTA_EXCEL}'.")
            return

        total_stats = {'inseridos': 0, 'atualizados': 0, 'ignorados': 0, 'identificados': 0}

        for arquivo in arquivos:
            try:
                stats = self._processar_arquivo(arquivo)
                if stats:
                    total_stats['inseridos'] += stats['inseridos']
                    total_stats['atualizados'] += stats['atualizados']
                    total_stats['ignorados'] += stats['ignorados']
                    total_stats['identificados'] += stats['identificados']
            except Exception as e:
                print(f"❌ Erro ao importar {arquivo}: {e}")

        print("\n📊 RESUMO TOTAL:")
        print(f"   ➕ Total inseridos   : {total_stats['inseridos']}")
        print(f"   ⏭️ Total ignorados  : {total_stats['ignorados']}")
        print(f"   ✅ Total de códigos não identificados processados: {total_stats['identificados']}")
        
        # Se algum código não identificado foi processado, notificar para atualizar a interface
        if total_stats['identificados'] > 0 and self.status_callback:
            self.status_callback(None, "ATUALIZAR_CODIGOS_NAO_IDENTIFICADOS")