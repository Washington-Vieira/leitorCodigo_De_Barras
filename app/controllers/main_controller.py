import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import sqlite3
import shutil
import os
from datetime import datetime
from app.models.produto import Produto
from app.models.leitura import Leitura
from app.models.caixa import Caixa
from app.models.codigo_nao_identificado import CodigoNaoIdentificado
from app.utils.excel_handler import ExcelHandler
from app.utils.excel_importer import ExcelImporter
from app.models.database import Database
from app.config import EXCEL_DIR
from app.controllers.resumo_controller import ResumoController
from app.views.main_view import LoadingDialog
from app.views.caixa_dialog import CaixaDialog

class MainController:
    def __init__(self, view=None):
        self.view = view
        self.excel_handler = ExcelHandler()
        self.excel_importer = ExcelImporter()
        self.excel_importer.set_callback(self.atualizar_status_interface)
        self.caixa_atual = None
        self.atualizar_status_caixa()
        
        # Configurar callback para códigos não identificados
        CodigoNaoIdentificado.set_callback(self.atualizar_status_interface)

        self.itens_sem_caixa_controller = None

    def set_itens_sem_caixa_controller(self, controller):
        """Define o controlador de itens sem caixa"""
        self.itens_sem_caixa_controller = controller

    def processar_codigo_identificado(self, serial, mostrar_mensagem=True):
        """Processa um código que foi identificado e o adiciona à tela principal"""
        # Verificar se o código já está na tabela principal
        for item in self.view.tree.get_children():
            valores = self.view.tree.item(item)['values']
            if valores and len(valores) > 2 and valores[2] == serial:
                # Código já está na tabela, não precisa adicionar novamente
                return True
        
        # Buscar informações do produto no banco
        produto = Produto.buscar_por_serial(serial)
        if produto:
            pedido, data_pedido, serial, item, maquina, linha_lida, quantidade, qtd_enviada, status, _, _ = produto
            
            # Buscar a data e hora originais da leitura não identificada
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT data_leitura, hora_leitura
                    FROM codigos_nao_identificados
                    WHERE serial = ?
                ''', (serial,))
                resultado = cursor.fetchone()
                if resultado:
                    data_leitura_original, hora_leitura_original = resultado
                else:
                    data_leitura_original = datetime.now().strftime('%Y-%m-%d')
                    hora_leitura_original = datetime.now().strftime('%H:%M:%S')
                
                # Verificar se já existe na tabela leituras
                cursor.execute('SELECT id FROM leituras WHERE serial = ?', (serial,))
                leitura_existente = cursor.fetchone()
                
                if not leitura_existente:
                    # Inserir na tabela leituras com a data/hora original
                    cursor.execute('''
                        INSERT INTO leituras (
                            serial, pedido_lido, linha_lida, 
                            data_leitura, hora_leitura,
                            status_caixa, numero_caixa
                        ) VALUES (?, ?, ?, ?, ?, 'SEM_CAIXA', NULL)
                    ''', (
                        serial, pedido, linha_lida,
                        data_leitura_original, hora_leitura_original
                    ))
                    conn.commit()
                    print(f"✓ Leitura inserida para o código {serial}")
                
                # Atualizar o status do código não identificado
                sucesso, mensagem = CodigoNaoIdentificado.atualizar_status(
                    serial,
                    identificado=True,
                    observacao="Identificado e processado automaticamente"
                )
                
                if not sucesso:
                    print(f"⚠️ Aviso ao processar código: {mensagem}")
                    return False
                
                # Limpar seleção atual na tabela principal
                self.view.tree.selection_clear()
                
                # Inserir na tabela principal
                novo_item = self.view.tree.insert("", 0, values=(
                    pedido, data_pedido, serial, item, maquina, linha_lida,
                    quantidade, qtd_enviada, status, 
                    f"{datetime.strptime(data_leitura_original, '%Y-%m-%d').strftime('%d/%m/%Y')} {hora_leitura_original}",
                    "-", ""  # Sem caixa atribuída
                ), tags=("identificado", "sem_caixa"))
                
                # Selecionar e mostrar o novo item na tabela principal
                self.view.tree.selection_set(novo_item)
                self.view.tree.see(novo_item)
                
                # Forçar atualização da interface principal
                self.view.root.update_idletasks()
                self.view.root.update()
                
                # Atualizar a tela de códigos não identificados se estiver aberta
                if hasattr(self, 'codigos_nao_identificados_view'):
                    self.codigos_nao_identificados_view.atualizar_lista()
                    self.codigos_nao_identificados_view.window.update_idletasks()
                
                # Atualizar e mostrar a tela de itens sem caixa
                if self.itens_sem_caixa_controller:
                    self.itens_sem_caixa_controller.atualizar_dados()
                    self.itens_sem_caixa_controller.mostrar_view()
                
                print(f"✨ Código {serial} identificado e adicionado à interface")
                
                # Mostrar mensagem apenas se solicitado e se o código não estava na tabela
                if mostrar_mensagem:
                    # Aguardar 1 segundo antes de mostrar a mensagem
                    self.view.root.after(1000, lambda s=serial, p=pedido, i=item, m=maquina, st=status, ni=novo_item: 
                        self._mostrar_mensagem_identificacao_sem_caixa(s, p, i, m, st, ni))
                
                return True
            finally:
                conn.close()
        return False
        
    def _mostrar_mensagem_identificacao_sem_caixa(self, serial, pedido, item, maquina, status, item_tree):
        """Mostra a mensagem de identificação para códigos sem caixa e pergunta se deseja atribuir uma caixa"""
        try:
            resposta = messagebox.askyesno(
                "Código Identificado",
                f"✅ O código {serial} foi identificado com sucesso!\n\n"
                f"📋 Informações do código:\n"
                f"• Pedido: {pedido}\n"
                f"• Item: {item}\n"
                f"• Máquina: {maquina}\n"
                f"• Status: {status}\n\n"
                "O código foi adicionado à lista de itens sem caixa.\n"
                "Deseja atribuir uma caixa agora?"
            )
            
            if resposta:
                # Mostrar a tela de itens sem caixa
                self.mostrar_itens_sem_caixa()
            
            # Verificar se o item ainda existe antes de tentar selecioná-lo
            if item_tree in self.view.tree.get_children():
                self.view.tree.selection_set(item_tree)
                self.view.tree.see(item_tree)
                self.view.tree.focus(item_tree)
                
                # Forçar atualização da interface
                self.view.root.update_idletasks()
                self.view.root.update()
        except Exception as e:
            print(f"Erro ao mostrar mensagem de identificação: {str(e)}")

    def atualizar_status_interface(self, serial, novo_status):
        """Atualiza o status de um item na interface quando ele muda no banco"""
        if novo_status == "ATUALIZAR_CODIGOS_NAO_IDENTIFICADOS":
            # Atualizar a tela de códigos não identificados se estiver aberta
            if hasattr(self, 'codigos_nao_identificados_view'):
                self.codigos_nao_identificados_view.atualizar_lista()
            return
            
        if novo_status == "ATUALIZAR_ITENS_SEM_CAIXA":
            # Atualizar a tela de itens sem caixa se estiver aberta
            if self.itens_sem_caixa_controller:
                self.itens_sem_caixa_controller.atualizar_dados()
            return
            
        if novo_status == "CODIGO_IDENTIFICADO":
            # Evitar processamento recursivo verificando se o código já está na tabela
            for item in self.view.tree.get_children():
                valores = self.view.tree.item(item)['values']
                if valores and len(valores) > 2 and valores[2] == serial:
                    return  # Se já existe na tabela, não processa novamente
            
            self.processar_codigo_identificado(serial, mostrar_mensagem=True)
            
            # Atualizar a tela de itens sem caixa se estiver aberta
            if self.itens_sem_caixa_controller:
                self.itens_sem_caixa_controller.atualizar_dados()
            return
            
        # Procurar o item na interface
        for item in self.view.tree.get_children():
            valores = self.view.tree.item(item)['values']
            if valores[2] == serial:  # índice 2 é o serial
                # Atualizar o status (índice 8)
                valores[8] = novo_status
                self.view.tree.item(item, values=valores)
                print(f"✨ Status atualizado na interface - Serial: {serial}, Novo status: {novo_status}")
                
                # Atualizar a tela de itens sem caixa se estiver aberta
                if self.itens_sem_caixa_controller:
                    self.itens_sem_caixa_controller.atualizar_dados()

    def atualizar_status_caixa(self):
        """Atualiza o status da caixa atual"""
        self.caixa_atual = Caixa.get_caixa_atual()
        if self.view:
            self.view.atualizar_status_caixa(self.caixa_atual)

    def abrir_caixa(self):
        """Abre uma nova caixa"""
        if self.caixa_atual:
            messagebox.showwarning("Atenção", 
                f"Já existe uma caixa aberta: {self.caixa_atual}\n"
                "Feche a caixa atual antes de abrir uma nova.")
            return
        
        dialog = CaixaDialog(self.view.root)
        numero_caixa = dialog.mostrar()
        
        if numero_caixa:
            sucesso, mensagem = Caixa.abrir_caixa(numero_caixa)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.atualizar_status_caixa()
            else:
                messagebox.showerror("Erro", mensagem)

    def abrir_caixas_fechadas(self):
        """Abre a tela de caixas fechadas"""
        self.mostrar_caixas_fechadas()

    def fechar_caixa(self):
        """Fecha a caixa atual"""
        if not self.caixa_atual:
            messagebox.showwarning("Atenção", "Não há caixa aberta para fechar.")
            return
        
        if messagebox.askyesno("Confirmar", 
            f"Deseja realmente fechar a caixa {self.caixa_atual}?"):
            
            sucesso, mensagem = Caixa.fechar_caixa()
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.atualizar_status_caixa()
                
                # Abrir tela de caixas fechadas
                self.mostrar_caixas_fechadas()
                
                # Limpar a tabela principal
                for item in self.view.tree.get_children():
                    self.view.tree.delete(item)
            else:
                messagebox.showerror("Erro", mensagem)

    def _processar_leitura(self, produto):
        """Processa a leitura de um produto e adiciona na tabela"""
        if not self.caixa_atual:
            messagebox.showwarning("Atenção", 
                "Não há caixa aberta.\nAbra uma caixa antes de fazer leituras.")
            return False
            
        pedido_lido, data_pedido, serial, item, maquina, linha_lida, quantidade, \
        qtd_enviada, status, data_leitura, hora_leitura = produto
        
        # Preparar dados para inserção na tabela leituras
        data_atual = datetime.now().strftime('%Y-%m-%d')
        hora_atual = datetime.now().strftime('%H:%M:%S')
        
        # Inserir na tabela leituras usando os dados corretos
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leituras (
                serial, pedido_lido, linha_lida, data_leitura, hora_leitura,
                numero_caixa, status_caixa
            ) VALUES (?, ?, ?, ?, ?, ?, "ABERTA")
        ''', (serial, pedido_lido, linha_lida, data_atual, hora_atual, self.caixa_atual))
        conn.commit()
        conn.close()
        
        # Calcular diferença de dias
        if data_pedido and data_atual:
            data_pedido_dt = datetime.strptime(data_pedido, '%d/%m/%Y')
            data_leitura_dt = datetime.strptime(data_atual, '%Y-%m-%d')
            diferenca_dias = (data_leitura_dt - data_pedido_dt).days
            data_hora = f"{datetime.now().strftime('%d/%m/%Y')} {hora_atual}"
        else:
            diferenca_dias = "-"
            data_hora = "-"
        
        # Inserir na tabela da interface com todos os dados corretos
        self.view.tree.insert("", 0, values=(
            pedido_lido, data_pedido, serial, item, maquina, linha_lida,
            quantidade, qtd_enviada, status, data_hora, diferenca_dias,
            self.caixa_atual
        ), tags=("aberta",))
        
        return True

    def inicializar(self):
        """Inicializa o controlador e carrega os dados iniciais"""
        print(f"📂 Verificando arquivos na pasta: {EXCEL_DIR}")
        self.excel_importer.importar_excels()
        
        # Verificar se a view está pronta antes de carregar os dados
        if hasattr(self, 'view') and hasattr(self.view, 'tree'):
            # Carregar códigos não identificados que foram processados
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    SELECT serial FROM codigos_nao_identificados 
                    WHERE status = 'IDENTIFICADO'
                ''')
                
                codigos_identificados = cursor.fetchall()
                for (serial,) in codigos_identificados:
                    self.processar_codigo_identificado(serial)
            finally:
                conn.close()
            
            # Carregar dados normais
            self.carregar_dados_iniciais()
            self.atualizar_status_caixa()

    def carregar_dados_iniciais(self):
        """Carrega os dados iniciais na tabela"""
        if not hasattr(self, 'view') or not hasattr(self.view, 'tree'):
            print("⚠️ View não está pronta para carregar dados")
            return
            
        # Limpar a tabela
        for item in self.view.tree.get_children():
            self.view.tree.delete(item)
            
        # Carregar dados do banco
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Primeiro, buscar códigos identificados que ainda não foram atribuídos a uma caixa
            cursor.execute('''
                SELECT 
                    p.pedido,
                    p.data_pedido,
                    p.serial,
                    p.item,
                    p.maquina,
                    p.linha_ato,
                    p.quantidade,
                    p.quantidade as qtd_enviada,
                    p.nome_status,
                    c.data_identificacao,
                    c.hora_identificacao,
                    NULL as numero_caixa,
                    'IDENTIFICADO' as status_caixa
                FROM produtos p
                INNER JOIN codigos_nao_identificados c ON p.serial = c.serial
                WHERE c.status = 'IDENTIFICADO'
                AND c.numero_caixa IS NULL
                AND c.data_identificacao = ?
            ''', (datetime.now().strftime('%Y-%m-%d'),))
            
            for row in cursor.fetchall():
                pedido, data_pedido, serial, item, maquina, linha_ato, quantidade, \
                qtd_enviada, status, data_leitura, hora_leitura, numero_caixa, status_caixa = row
                
                # Calcular diferença de dias
                if data_pedido and data_leitura:
                    data_pedido_dt = datetime.strptime(data_pedido, '%d/%m/%Y')
                    data_leitura_dt = datetime.strptime(data_leitura, '%Y-%m-%d')
                    diferenca_dias = (data_leitura_dt - data_pedido_dt).days
                    data_hora = f"{datetime.strptime(data_leitura, '%Y-%m-%d').strftime('%d/%m/%Y')} {hora_leitura}"
                else:
                    diferenca_dias = "-"
                    data_hora = "-"
                
                # Extrair os primeiros 4 caracteres da linha_ato para linha_lida
                linha_lida = linha_ato[:4] if linha_ato else ''
                
                # Inserir na tabela com tags para colorização
                self.view.tree.insert("", "end", values=(
                    pedido, data_pedido, serial, item, maquina, linha_lida,
                    quantidade, qtd_enviada, status, data_hora, diferenca_dias,
                    numero_caixa
                ), tags=("identificado",))
            
            # Depois, buscar itens da caixa atual que está aberta
            if self.caixa_atual:
                cursor.execute('''
                    SELECT 
                        l.pedido_lido,
                        p.data_pedido,
                        l.serial,
                        p.item,
                        p.maquina,
                        l.linha_lida,
                        p.quantidade,
                        (SELECT SUM(pp.quantidade) FROM produtos pp WHERE pp.serial = l.serial),
                        p.nome_status,
                        l.data_leitura,
                        l.hora_leitura,
                        l.numero_caixa,
                        l.status_caixa
                    FROM leituras l
                    LEFT JOIN produtos p ON l.serial = p.serial
                    LEFT JOIN caixas c ON l.numero_caixa = c.numero_caixa
                    WHERE l.numero_caixa = ? AND l.status_caixa = "ABERTA"
                    ORDER BY l.data_leitura DESC, l.hora_leitura DESC
                ''', (self.caixa_atual,))
                
                for row in cursor.fetchall():
                    pedido, data_pedido, serial, item, maquina, linha_lida, quantidade, \
                    qtd_enviada, status, data_leitura, hora_leitura, numero_caixa, status_caixa = row
                    
                    # Calcular diferença de dias
                    if data_pedido and data_leitura:
                        data_pedido_dt = datetime.strptime(data_pedido, '%d/%m/%Y')
                        data_leitura_dt = datetime.strptime(data_leitura, '%Y-%m-%d')
                        diferenca_dias = (data_leitura_dt - data_pedido_dt).days
                        data_hora = f"{datetime.strptime(data_leitura, '%Y-%m-%d').strftime('%d/%m/%Y')} {hora_leitura}"
                    else:
                        diferenca_dias = "-"
                        data_hora = "-"
                    
                    # Inserir na tabela com tags para colorização
                    self.view.tree.insert("", "end", values=(
                        pedido, data_pedido, serial, item, maquina, linha_lida,
                        quantidade, qtd_enviada, status, data_hora, diferenca_dias,
                        numero_caixa
                    ), tags=("aberta",))
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {str(e)}")
        finally:
            conn.close()
        
        # Configurar cores das linhas
        if hasattr(self.view, 'configurar_cores_linhas'):
            self.view.configurar_cores_linhas()

    def verificar_codigo(self, event):
        """Verifica o código lido e processa conforme necessário"""
        codigo_original = self.view.entry_codigo.get().strip()
        if not codigo_original:
            return
        
        # Remover o primeiro caractere da esquerda apenas se for '0'
        codigo = codigo_original[1:] if len(codigo_original) > 1 and codigo_original[0] == '0' else codigo_original
        
        # Limpar campo de entrada
        self.view.entry_codigo.delete(0, tk.END)
        
        # Verificar se o código existe no banco
        produto = Produto.buscar_por_serial(codigo)
        
        if not produto:
            # Verificar se já está registrado como não identificado
            status_existente = CodigoNaoIdentificado.verificar_se_existe(codigo)
            
            if status_existente == 'PENDENTE':
                messagebox.showwarning(
                    "Código Não Identificado",
                    "Este código já está registrado como não identificado e aguarda processamento."
                )
            elif status_existente == 'IDENTIFICADO':
                messagebox.showinfo(
                    "Código Já Processado",
                    "Este código já foi processado anteriormente."
                )
            else:
                # Registrar novo código não identificado
                sucesso, mensagem = CodigoNaoIdentificado.registrar_codigo(codigo)
                if sucesso:
                    messagebox.showinfo(
                        "Código Registrado",
                        "Código não identificado foi registrado e será processado posteriormente."
                    )
                else:
                    messagebox.showerror("Erro", mensagem)
            return
        
        # Se o código existe, verificar se já foi lido
        if Leitura.verificar_se_ja_lido(codigo):
            messagebox.showwarning(
                "Aviso",
                "Este código já foi lido anteriormente!"
            )
            return
            
        # Verificar se há uma caixa aberta
        caixa_atual = Caixa.get_caixa_atual()
        if not caixa_atual:
            messagebox.showwarning(
                "Aviso",
                "Não há caixa aberta! Por favor, abra uma caixa primeiro."
            )
            return
            
        # Processar a leitura
        pedido, data_pedido, serial, item, maquina, linha_lida, quantidade, qtd_enviada, status, _, _ = produto
        
        # Inserir leitura
        Leitura.inserir_leitura(serial, pedido, linha_lida)
        
        # Atualizar leitura com a caixa atual
        Caixa.atualizar_leitura_com_caixa(serial, caixa_atual)
        
        # Verificar se o código estava registrado como não identificado
        status_nao_identificado = CodigoNaoIdentificado.verificar_se_existe(serial)
        if status_nao_identificado:
            # Atualizar status do código não identificado
            CodigoNaoIdentificado.atualizar_status(
                serial,
                identificado=True,
                numero_caixa=caixa_atual,
                observacao="Identificado e processado automaticamente"
            )
        
        # Atualizar interface
        self.atualizar_dados()
        
        # Feedback sonoro usando o método correto
        self.view.root.bell()

    def atualizar_dados(self):
        """Atualiza os dados na interface"""
        # Guardar os códigos identificados antes de atualizar
        codigos_identificados = []
        for item in self.view.tree.get_children():
            valores = self.view.tree.item(item)['values']
            if valores and len(valores) > 2:  # Garantir que há valores suficientes
                serial = valores[2]  # índice 2 é o serial
                tags = self.view.tree.item(item)['tags']
                if 'identificado' in tags:
                    codigos_identificados.append(serial)
        
        # Atualizar a tabela
        self.view.atualizar_tabela()
        
        # Reprocessar os códigos identificados sem mostrar mensagem
        for serial in codigos_identificados:
            self.processar_codigo_identificado(serial, mostrar_mensagem=False)
        
        # Atualizar status da caixa
        self.view.atualizar_status_caixa(self.caixa_atual)

    def remover_leitura(self, event=None):
        """Remove uma leitura selecionada completamente de todas as tabelas do sistema"""
        if not hasattr(self, 'view') or not self.view:
            return
            
        item_selecionado = self.view.tree.selection()
        
        if not item_selecionado:
            messagebox.showwarning("Atenção", "Por favor, selecione um item para remover.")
            return
            
        if messagebox.askyesno("Confirmar Remoção", 
                           "Tem certeza que deseja remover esta leitura?\n"
                           "Esta ação não pode ser desfeita e o registro será excluído completamente do sistema."):
            
            item = self.view.tree.item(item_selecionado[0])
            valores = item['values']
            
            # Extrair o serial do item selecionado
            serial = valores[2]  # índice 2 é o serial
            
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                try:
                    # Primeiro, verificar se existem registros nas tabelas
                    cursor.execute('SELECT COUNT(*) FROM leituras WHERE serial = ?', (serial,))
                    count_leituras = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM codigos_nao_identificados WHERE serial = ?', (serial,))
                    count_nao_identificados = cursor.fetchone()[0]
                    
                    # Remover TODOS os registros relacionados ao serial
                    
                    # 1. Remover da tabela leituras
                    cursor.execute('DELETE FROM leituras WHERE serial = ?', (serial,))
                    leituras_removidas = cursor.rowcount
                    
                    # 2. Remover da tabela codigos_nao_identificados
                    cursor.execute('DELETE FROM codigos_nao_identificados WHERE serial = ?', (serial,))
                    nao_identificados_removidos = cursor.rowcount
                    
                    # 3. Remover quaisquer referências em outras tabelas relacionadas
                    # Tabela de caixas (se houver referência)
                    cursor.execute('''
                        UPDATE caixas 
                        SET quantidade = quantidade - 1 
                        WHERE numero_caixa IN (
                            SELECT DISTINCT numero_caixa 
                            FROM leituras 
                            WHERE serial = ? AND numero_caixa IS NOT NULL
                        )
                    ''', (serial,))
                    
                    conn.commit()
                    
                    # Log detalhado das remoções
                    print(f"📊 Estatísticas de remoção para o serial {serial}:")
                    print(f"✓ Registros encontrados em leituras: {count_leituras}")
                    print(f"✓ Registros encontrados em codigos_nao_identificados: {count_nao_identificados}")
                    print(f"✓ Registros removidos de leituras: {leituras_removidas}")
                    print(f"✓ Registros removidos de codigos_nao_identificados: {nao_identificados_removidos}")
                    
                    # Mensagem de sucesso com detalhes
                    mensagem = f"✅ Código {serial} removido com sucesso!\n\n"
                    mensagem += f"Registros removidos:\n"
                    mensagem += f"• Tabela leituras: {leituras_removidas}\n"
                    mensagem += f"• Tabela códigos não identificados: {nao_identificados_removidos}"
                    
                    messagebox.showinfo("Sucesso", mensagem)
                    
                    # Atualizar TODAS as interfaces
                    self.carregar_dados_iniciais()  # Recarrega a tabela principal do zero
                    
                    # Atualizar a tela de códigos não identificados
                    if hasattr(self, 'codigos_nao_identificados_view'):
                        self.codigos_nao_identificados_view.atualizar_lista()
                    
                    # Atualizar a tela de itens sem caixa
                    if self.itens_sem_caixa_controller:
                        self.itens_sem_caixa_controller.atualizar_dados()
                        
                    # Forçar atualização visual
                    if hasattr(self, 'view') and self.view:
                        self.view.root.update_idletasks()
                    
                except Exception as e:
                    conn.rollback()
                    raise e
                finally:
                    conn.close()
                    
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro ao remover registros:\n{str(e)}")

    def abrir_resumo_pendentes(self):
        from app.views.resumo_view import ResumoView
        controller = ResumoController("PENDENTE")
        view = ResumoView(controller, "PENDENTE")
        controller.view = view
        controller.filtrar_resumo("")

    def abrir_resumo_andamento(self):
        from app.views.resumo_view import ResumoView
        controller = ResumoController("EM ANDAMENTO")
        view = ResumoView(controller, "EM ANDAMENTO")
        controller.view = view
        controller.filtrar_resumo("")

    def abrir_resumo_concluidos(self):
        from app.views.resumo_view import ResumoView
        controller = ResumoController("CONCLUÍDO")
        view = ResumoView(controller, "CONCLUÍDO")
        controller.view = view
        controller.filtrar_resumo("")

    def exportar_excel(self):
        self.excel_handler.exportar_para_excel(self.view.tree, "dados_exportados.xlsx")

    def exportar_controladoria(self, data_selecionada=None):
        """Exporta relatório consolidado para a controladoria"""
        if self.excel_handler.exportar_relatorio_controladoria(data_selecionada):
            messagebox.showinfo("Sucesso", "✅ Relatório de controladoria gerado com sucesso!")
        else:
            messagebox.showerror("Erro", "❌ Erro ao gerar relatório de controladoria.")

    def importar_planilha(self):
        """Permite ao usuário selecionar uma planilha para importar"""
        arquivo = filedialog.askopenfilename(
            title="Selecione a planilha para importar",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
        )
        
        if arquivo:
            try:
                # Mostrar diálogo de loading
                loading = LoadingDialog(self.view.root, "Importando planilha...")
                self.view.root.update()
                
                try:
                    # Copiar arquivo para a pasta de importação
                    nome_arquivo = os.path.basename(arquivo)
                    loading.update_message(f"Copiando arquivo {nome_arquivo}...")
                    destino = os.path.join(EXCEL_DIR, nome_arquivo)
                    shutil.copy2(arquivo, destino)
                    
                    # Importar o arquivo
                    loading.update_message(f"Processando dados do arquivo...")
                    stats = self.excel_importer._processar_arquivo(nome_arquivo)
                    
                    # Fechar diálogo de loading
                    loading.close()
                    
                    if stats:
                        # Buscar códigos não identificados que foram processados
                        conn = sqlite3.connect(Database.DB_NAME)
                        cursor = conn.cursor()
                        
                        try:
                            cursor.execute('''
                                SELECT serial FROM codigos_nao_identificados 
                                WHERE status = 'IDENTIFICADO'
                                AND data_identificacao = ?
                            ''', (datetime.now().strftime('%Y-%m-%d'),))
                            
                            codigos_identificados = cursor.fetchall()
                            
                            # Processar cada código identificado
                            for (serial,) in codigos_identificados:
                                self.processar_codigo_identificado(serial)
                                
                        finally:
                            conn.close()
                        
                        # Mostrar mensagem de sucesso
                        self.view.root.after(1000, lambda: messagebox.showinfo(
                            "Importação Concluída", 
                            f"✅ Importação concluída com sucesso!\n\n"
                            f"➕ Registros inseridos: {stats['inseridos']}\n"
                            f"⏭️ Registros ignorados: {stats['ignorados']}\n"
                            f"✨ Códigos não identificados processados: {stats['identificados']}"
                        ))
                        
                except Exception as e:
                    loading.close()
                    raise e
                    
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro ao importar arquivo:\n{str(e)}")

    def mostrar_caixas_fechadas(self):
        """Mostra a tela de caixas fechadas"""
        if not hasattr(self, 'caixas_fechadas_controller'):
            from app.controllers.caixas_fechadas_controller import CaixasFechadasController
            self.caixas_fechadas_controller = CaixasFechadasController()
            self.caixas_fechadas_controller.set_main_controller(self)  # Configurar referência
        
        self.caixas_fechadas_controller.mostrar_view()

    def atualizar_tela_leituras(self):
        """Atualiza a tabela de leituras"""
        if hasattr(self, 'view') and self.view:
            self.carregar_dados_iniciais()

    def mostrar_itens_sem_caixa(self):
        """Mostra a tela de itens sem caixa"""
        if not self.itens_sem_caixa_controller:
            from app.controllers.itens_sem_caixa_controller import ItensSemCaixaController
            self.itens_sem_caixa_controller = ItensSemCaixaController()
            self.itens_sem_caixa_controller.set_main_controller(self)
        
        self.itens_sem_caixa_controller.mostrar_view()
    
    def verificar_itens_sem_caixa(self):
        """Verifica se existem itens sem caixa e mostra a tela se necessário"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) 
            FROM leituras 
            WHERE numero_caixa IS NULL
        ''')
        
        total = cursor.fetchone()[0]
        conn.close()
        
        if total > 0:
            if messagebox.askyesno("Atenção",
                f"Existem {total} itens que não estão em nenhuma caixa.\n"
                "Deseja visualizar esses itens agora?"):
                self.mostrar_itens_sem_caixa()

    def mostrar_codigos_nao_identificados(self):
        """Mostra a tela de códigos não identificados"""
        if not hasattr(self, 'codigos_nao_identificados_view'):
            from app.views.codigos_nao_identificados_view import CodigosNaoIdentificadosView
            self.codigos_nao_identificados_view = CodigosNaoIdentificadosView(self.view.root, self)
        else:
            self.codigos_nao_identificados_view.window.deiconify()
            self.codigos_nao_identificados_view.window.lift()
            self.codigos_nao_identificados_view.atualizar_lista()