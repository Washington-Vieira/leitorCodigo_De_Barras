import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from app.models.database import Database
from app.views.itens_sem_caixa_view import ItensSemCaixaView
from app.views.selecionar_caixa_dialog import SelecionarCaixaDialog

class ItensSemCaixaController:
    def __init__(self):
        self.view = None
        self.main_controller = None
    
    def set_main_controller(self, controller):
        """Define a referência ao controlador principal"""
        self.main_controller = controller
    
    def mostrar_view(self):
        """Mostra a tela de itens sem caixa"""
        if not self.view:
            from app.views.itens_sem_caixa_view import ItensSemCaixaView
            self.view = ItensSemCaixaView(self)
        else:
            self.view.window.deiconify()
            self.view.window.lift()
            self.atualizar_dados()
    
    def atualizar_dados(self):
        """Atualiza os dados na tabela"""
        if not self.view:
            return
            
        # Limpar tabela
        for item in self.view.tree.get_children():
            self.view.tree.delete(item)
            
        # Buscar itens sem caixa
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Primeiro, buscar todos os códigos que foram identificados hoje
            data_atual = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT DISTINCT
                    l.serial,
                    l.pedido_lido,
                    p.item,
                    p.maquina,
                    l.linha_lida,
                    p.quantidade,
                    l.data_leitura,
                    l.hora_leitura,
                    p.nome_status,
                    CASE 
                        WHEN c.status = 'IDENTIFICADO' THEN 'Identificado hoje'
                        ELSE l.status_caixa 
                    END as status_item,
                    c.data_identificacao
                FROM leituras l
                LEFT JOIN produtos p ON l.serial = p.serial
                LEFT JOIN codigos_nao_identificados c ON l.serial = c.serial
                WHERE (
                    -- Códigos sem caixa na tabela de leituras
                    l.numero_caixa IS NULL 
                    OR l.status_caixa = 'SEM_CAIXA'
                    OR TRIM(COALESCE(l.numero_caixa, '')) = ''
                )
                OR (
                    -- Códigos identificados hoje na tabela de códigos não identificados
                    c.status = 'IDENTIFICADO' 
                    AND c.data_identificacao = ?
                    AND (c.numero_caixa IS NULL OR TRIM(c.numero_caixa) = '')
                )
                ORDER BY 
                    CASE 
                        WHEN c.status = 'IDENTIFICADO' AND c.data_identificacao = ? THEN 1
                        WHEN l.status_caixa = 'SEM_CAIXA' THEN 2
                        ELSE 3 
                    END,
                    l.data_leitura DESC, 
                    l.hora_leitura DESC
            ''', (data_atual, data_atual))
            
            total_itens = 0
            for row in cursor.fetchall():
                serial, pedido, item, maquina, linha_lida, quantidade, \
                data_leitura, hora_leitura, status, status_item, data_identificacao = row
                
                # Formatar data para exibição (YYYY-MM-DD -> DD/MM/YYYY)
                data_formatada = datetime.strptime(data_leitura, '%Y-%m-%d').strftime('%d/%m/%Y')
                
                # Definir tags para colorização
                if status_item == 'Identificado hoje':
                    tags = ("identificado_hoje",)
                    status_exibicao = "Identificado hoje"
                else:
                    tags = ("sem_caixa",)
                    status_exibicao = status
                
                self.view.tree.insert("", "end", values=(
                    serial, pedido, item, maquina, linha_lida,
                    quantidade, data_formatada, hora_leitura, status_exibicao
                ), tags=tags)
                
                total_itens += 1
                
            # Atualizar título da janela com o total de itens
            if self.view:
                self.view.atualizar_titulo(total_itens)
                
        except Exception as e:
            print(f"❌ Erro ao carregar itens sem caixa: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar itens sem caixa:\n{str(e)}")
        finally:
            conn.close()
    
    def atribuir_caixa(self, numero_caixa):
        """Atribui uma caixa aos itens selecionados"""
        if not self.view:
            return
            
        itens_selecionados = self.view.tree.selection()
        if not itens_selecionados:
            messagebox.showwarning("Atenção", "Selecione pelo menos um item para atribuir à caixa.")
            return
            
        # Verificar se a caixa existe e está aberta
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT status FROM caixas WHERE numero_caixa = ?', (numero_caixa,))
            resultado = cursor.fetchone()
            
            if not resultado:
                # Criar nova caixa
                data_atual = datetime.now().strftime('%Y-%m-%d')
                hora_atual = datetime.now().strftime('%H:%M:%S')
                
                cursor.execute('''
                    INSERT INTO caixas (numero_caixa, data_abertura, hora_abertura, status)
                    VALUES (?, ?, ?, 'ABERTA')
                ''', (numero_caixa, data_atual, hora_atual))
                
            elif resultado[0] == 'FECHADA':
                messagebox.showerror("Erro", f"A caixa {numero_caixa} está fechada. Não é possível adicionar itens.")
                return
            
            # Atualizar itens selecionados
            for item in itens_selecionados:
                valores = self.view.tree.item(item)['values']
                serial = valores[0]  # índice 0 é o serial
                
                # Atualizar na tabela de leituras
                cursor.execute('''
                    UPDATE leituras 
                    SET numero_caixa = ?, status_caixa = 'ABERTA'
                    WHERE serial = ?
                ''', (numero_caixa, serial))
                
                # Atualizar na tabela de códigos não identificados
                cursor.execute('''
                    UPDATE codigos_nao_identificados
                    SET numero_caixa = ?
                    WHERE serial = ? AND status = 'IDENTIFICADO'
                ''', (numero_caixa, serial))
            
            conn.commit()
            messagebox.showinfo("Sucesso", f"✅ Itens atribuídos à caixa {numero_caixa} com sucesso!")
            
            # Atualizar interfaces
            self.atualizar_dados()
            if self.main_controller:
                self.main_controller.atualizar_dados()
                # Atualizar a tela de códigos não identificados se estiver aberta
                if hasattr(self.main_controller, 'codigos_nao_identificados_view'):
                    self.main_controller.codigos_nao_identificados_view.atualizar_lista()
                
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao atribuir caixa: {str(e)}")
        finally:
            conn.close()
    
    def solicitar_numero_caixa(self):
        """Solicita o número da caixa para atribuição"""
        if not self.view:
            return
            
        from app.views.caixa_dialog import CaixaDialog
        dialog = CaixaDialog(self.view.window)
        numero_caixa = dialog.mostrar()
        
        if numero_caixa:
            self.atribuir_caixa(numero_caixa)
    
    def remover_item(self, event=None):
        """Remove o item selecionado de todas as tabelas"""
        if not self.view:
            return
            
        itens_selecionados = self.view.tree.selection()
        if not itens_selecionados:
            messagebox.showwarning("Atenção", "Selecione pelo menos um item para remover.")
            return
            
        if messagebox.askyesno("Confirmar Remoção", 
                           "Tem certeza que deseja remover este item?\n"
                           "Esta ação não pode ser desfeita e o registro será excluído completamente do sistema."):
            
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            try:
                for item in itens_selecionados:
                    valores = self.view.tree.item(item)['values']
                    serial = valores[0]  # índice 0 é o serial
                    
                    # Remover da tabela leituras
                    cursor.execute('DELETE FROM leituras WHERE serial = ?', (serial,))
                    leituras_removidas = cursor.rowcount
                    
                    # Remover da tabela codigos_nao_identificados
                    cursor.execute('DELETE FROM codigos_nao_identificados WHERE serial = ?', (serial,))
                    nao_identificados_removidos = cursor.rowcount
                    
                    print(f"✓ Removido da tabela leituras: {leituras_removidas} registro(s)")
                    print(f"✓ Removido da tabela codigos_nao_identificados: {nao_identificados_removidos} registro(s)")
                
                conn.commit()
                messagebox.showinfo("Sucesso", "✅ Item(ns) removido(s) com sucesso!")
                
                # Atualizar todas as interfaces
                self.atualizar_dados()
                if self.main_controller:
                    self.main_controller.carregar_dados_iniciais()
                    if hasattr(self.main_controller, 'codigos_nao_identificados_view'):
                        self.main_controller.codigos_nao_identificados_view.atualizar_lista()
                
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"❌ Erro ao remover item(ns):\n{str(e)}")
            finally:
                conn.close() 