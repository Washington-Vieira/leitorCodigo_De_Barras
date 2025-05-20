import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
from app.models.database import Database
from app.views.caixas_fechadas_view import CaixasFechadasView

class CaixasFechadasController:
    def __init__(self):
        self.view = None
        self.janela_detalhes = None  # Para controlar a janela de detalhes
        self.main_controller = None  # Referência ao controlador principal
    
    def set_main_controller(self, controller):
        """Define a referência ao controlador principal"""
        self.main_controller = controller
    
    def mostrar_view(self):
        """Cria e mostra a view de caixas fechadas"""
        try:
            # Criar a view se não existir
            if not self.view:
                self.view = CaixasFechadasView(self)
                
            # Garantir que a janela está visível
            self.view.window.deiconify()
            self.view.window.lift()
            
            # Carregar os dados
            self.carregar_caixas_fechadas()
            
        except Exception as e:
            print(f"Erro ao mostrar view: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir tela de caixas fechadas:\n{str(e)}")
    
    def carregar_caixas_fechadas(self):
        """Carrega todas as caixas fechadas do banco de dados"""
        try:
            # Verificar se a view existe
            if not self.view:
                print("View não inicializada")
                return
                
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''
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
                GROUP BY c.numero_caixa, c.total_itens, c.data_fechamento, 
                         c.hora_fechamento, c.usuario_fechamento
                ORDER BY c.data_fechamento DESC, c.hora_fechamento DESC
            ''')
            
            caixas = cursor.fetchall()
            conn.close()
            
            # Limpar tabela atual
            self.view.limpar_tabela()
            
            # Adicionar caixas à tabela
            for caixa in caixas:
                self.view.adicionar_caixa({
                    'numero_caixa': caixa[0],
                    'total_itens': caixa[5] or caixa[1],  # Usar contagem real ou total registrado
                    'data_fechamento': caixa[2],
                    'hora_fechamento': caixa[3],
                    'usuario_fechamento': caixa[4]
                })
                
            # Atualizar título da janela com total de caixas
            self.view.atualizar_titulo(len(caixas))
            
        except Exception as e:
            print(f"Erro ao carregar caixas fechadas: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar caixas fechadas:\n{str(e)}")
    
    def filtrar_caixas(self, event=None):
        """Filtra as caixas com base nos critérios de pesquisa"""
        texto_pesquisa = self.view.entry_pesquisa.get().lower()
        filtro_data = self.view.combo_data.get()
        
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        # Construir a query base
        query = '''
            SELECT 
                c.numero_caixa,
                c.total_itens,
                c.data_fechamento,
                c.hora_fechamento,
                COALESCE(c.usuario_fechamento, 'Sistema') as usuario_fechamento
            FROM caixas c
            WHERE c.status = 'FECHADA'
        '''
        
        params = []
        
        # Adicionar filtro de texto
        if texto_pesquisa:
            query += " AND (c.numero_caixa LIKE ? OR COALESCE(c.usuario_fechamento, 'Sistema') LIKE ?)"
            params.extend([f"%{texto_pesquisa}%", f"%{texto_pesquisa}%"])
        
        # Adicionar filtro de data
        hoje = datetime.now().date()
        if filtro_data == "Hoje":
            query += " AND c.data_fechamento = ?"
            params.append(hoje.strftime('%Y-%m-%d'))
        elif filtro_data == "Última semana":
            data_inicio = hoje - timedelta(days=7)
            query += " AND c.data_fechamento >= ?"
            params.append(data_inicio.strftime('%Y-%m-%d'))
        elif filtro_data == "Último mês":
            data_inicio = hoje - timedelta(days=30)
            query += " AND c.data_fechamento >= ?"
            params.append(data_inicio.strftime('%Y-%m-%d'))
        
        query += " ORDER BY c.data_fechamento DESC, c.hora_fechamento DESC"
        
        cursor.execute(query, params)
        caixas = cursor.fetchall()
        conn.close()
        
        # Atualizar tabela
        self.view.limpar_tabela()
        for caixa in caixas:
            self.view.adicionar_caixa({
                'numero_caixa': caixa[0],
                'total_itens': caixa[1],
                'data_fechamento': caixa[2],
                'hora_fechamento': caixa[3],
                'usuario_fechamento': caixa[4]
            })
    
    def visualizar_detalhes_caixa(self, event=None, numero_caixa=None):
        """Abre uma nova janela com os detalhes da caixa selecionada"""
        try:
            if numero_caixa is None:
                selecionado = self.view.tree.selection()
                if not selecionado:
                    messagebox.showwarning("Atenção", "Por favor, selecione uma caixa para visualizar os detalhes.")
                    return
                
                item = self.view.tree.item(selecionado[0])
                numero_caixa = item['values'][0]
            
            self.numero_caixa_atual = numero_caixa  # Armazenar para uso em outras funções
            
            # Se já existe uma janela de detalhes, destruí-la
            if self.janela_detalhes:
                self.janela_detalhes.destroy()
            
            # Criar janela de detalhes
            self.janela_detalhes = tk.Toplevel(self.view.window)
            self.janela_detalhes.title(f"Detalhes da Caixa {numero_caixa}")
            self.janela_detalhes.geometry("1000x600")
            
            # Centralizar a janela
            self.janela_detalhes.update_idletasks()
            width = self.janela_detalhes.winfo_width()
            height = self.janela_detalhes.winfo_height()
            x = (self.janela_detalhes.winfo_screenwidth() // 2) - (width // 2)
            y = (self.janela_detalhes.winfo_screenheight() // 2) - (height // 2)
            self.janela_detalhes.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame para informações da caixa
            frame_info = ttk.Frame(self.janela_detalhes, padding="10")
            frame_info.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(frame_info, 
                text=f"Caixa: {numero_caixa}", 
                font=("Arial", 12, "bold")
            ).pack(side="left", padx=5)
            
            # Frame para a tabela
            frame_tabela = ttk.Frame(self.janela_detalhes)
            frame_tabela.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Criar Treeview para itens
            colunas = ("Serial", "Pedido", "Item", "Máquina", "Linha", "Qtd Programada", 
                      "Qtd Enviada", "Data/Hora")
            self.tree_detalhes = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
            
            # Configurar colunas
            larguras = {
                "Serial": 150,
                "Pedido": 120,
                "Item": 250,
                "Máquina": 120,
                "Linha": 100,
                "Qtd Programada": 120,
                "Qtd Enviada": 120,
                "Data/Hora": 150
            }
            
            for col in colunas:
                self.tree_detalhes.heading(col, text=col)
                self.tree_detalhes.column(col, width=larguras.get(col, 120))
            
            # Adicionar scrollbars
            scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree_detalhes.yview)
            scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.tree_detalhes.xview)
            self.tree_detalhes.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            # Layout
            self.tree_detalhes.grid(row=0, column=0, sticky="nsew")
            scrollbar_y.grid(row=0, column=1, sticky="ns")
            scrollbar_x.grid(row=1, column=0, sticky="ew")
            
            # Configurar expansão
            frame_tabela.grid_rowconfigure(0, weight=1)
            frame_tabela.grid_columnconfigure(0, weight=1)
            
            # Frame para botões
            frame_botoes = ttk.Frame(self.janela_detalhes, padding="10")
            frame_botoes.pack(fill="x", padx=10, pady=5)
            
            ttk.Button(
                frame_botoes,
                text="🗑️ Excluir Item",
                command=self.excluir_item
            ).pack(side="left", padx=5)
            
            ttk.Button(
                frame_botoes,
                text="❌ Fechar",
                command=self.janela_detalhes.destroy
            ).pack(side="right", padx=5)
            
            # Criar menu de contexto para itens
            self.menu_contexto_itens = tk.Menu(self.janela_detalhes, tearoff=0)
            self.menu_contexto_itens.add_command(
                label="🗑️ Excluir Item",
                command=self.excluir_item
            )
            
            # Bindings para exclusão
            self.tree_detalhes.bind("<Delete>", lambda e: self.excluir_item())
            self.tree_detalhes.bind("<Button-3>", self.mostrar_menu_contexto_item)
            
            # Carregar itens da caixa
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            # Primeiro, buscar informações da caixa
            cursor.execute('''
                SELECT COUNT(*) as total_itens
                FROM leituras
                WHERE numero_caixa = ?
            ''', (numero_caixa,))
            total_itens_caixa = cursor.fetchone()[0]
            
            # Buscar itens da caixa com quantidades
            cursor.execute('''
                SELECT 
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
                    l.data_leitura || ' ' || l.hora_leitura
                FROM leituras l
                LEFT JOIN produtos p ON l.serial = p.serial
                WHERE l.numero_caixa = ?
                ORDER BY l.data_leitura, l.hora_leitura
            ''', (numero_caixa,))
            
            # Adicionar itens à tabela
            for item in cursor.fetchall():
                self.tree_detalhes.insert("", "end", values=item)
            
            # Atualizar informações no topo de forma simplificada
            info_label = tk.Label(frame_info, 
                text=f"Caixa {numero_caixa} - Total de Itens: {total_itens_caixa}",
                font=("Arial", 12, "bold"),
                fg="#1976D2"  # Azul
            )
            info_label.pack(side="left", padx=(20, 5))
            
            conn.close()
            
            # Configurar protocolo de fechamento
            self.janela_detalhes.protocol("WM_DELETE_WINDOW", 
                lambda: self.fechar_janela_detalhes())
            
        except Exception as e:
            print(f"Erro ao visualizar detalhes: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao visualizar detalhes:\n{str(e)}")
    
    def fechar_janela_detalhes(self):
        """Fecha a janela de detalhes e limpa a referência"""
        if self.janela_detalhes:
            self.janela_detalhes.destroy()
            self.janela_detalhes = None
    
    def exportar_relatorio(self):
        """Exporta os dados filtrados para um arquivo Excel"""
        from app.utils.excel_handler import ExcelHandler
        
        # Obter dados da tabela
        dados = []
        for item in self.view.tree.get_children():
            valores = self.view.tree.item(item)['values']
            dados.append({
                'Número da Caixa': valores[0],
                'Total de Itens': valores[1],
                'Data de Fechamento': valores[2],
                'Hora de Fechamento': valores[3],
                'Fechado por': valores[4]
            })
        
        if dados:
            try:
                excel_handler = ExcelHandler()
                if excel_handler.exportar_relatorio_caixas(dados):
                    messagebox.showinfo("Sucesso", "✅ Relatório exportado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro ao exportar relatório:\n{str(e)}")
        else:
            messagebox.showwarning("Atenção", "Não há dados para exportar.")
    
    def exportar_por_periodo(self):
        """Abre diálogo para selecionar período e exporta relatório"""
        from datetime import datetime
        from tkcalendar import DateEntry
        import tkinter as tk
        from tkinter import ttk
        
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.view.window)
        dialog.title("Exportar por Período")
        dialog.geometry("400x200")
        
        # Centralizar a janela
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Data inicial
        ttk.Label(frame, text="Data Inicial:").grid(row=0, column=0, padx=5, pady=5)
        data_inicial = DateEntry(frame, width=12, background='darkblue',
                               foreground='white', borderwidth=2, locale='pt_BR')
        data_inicial.grid(row=0, column=1, padx=5, pady=5)
        
        # Data final
        ttk.Label(frame, text="Data Final:").grid(row=1, column=0, padx=5, pady=5)
        data_final = DateEntry(frame, width=12, background='darkblue',
                             foreground='white', borderwidth=2, locale='pt_BR')
        data_final.grid(row=1, column=1, padx=5, pady=5)
        
        def exportar():
            try:
                from app.utils.excel_handler import ExcelHandler
                excel_handler = ExcelHandler()
                
                # Converter datas para datetime
                data_inicio = datetime.strptime(data_inicial.get(), '%d/%m/%Y')
                data_fim = datetime.strptime(data_final.get(), '%d/%m/%Y')
                
                if data_inicio > data_fim:
                    messagebox.showerror("Erro", "Data inicial não pode ser maior que a data final!")
                    return
                
                if excel_handler.exportar_relatorio_caixas_por_data(data_inicio, data_fim):
                    messagebox.showinfo("Sucesso", "✅ Relatório exportado com sucesso!")
                    dialog.destroy()
                else:
                    messagebox.showwarning("Atenção", "Nenhum dado encontrado para o período selecionado.")
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro ao exportar relatório:\n{str(e)}")
        
        # Botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(frame_botoes, text="Exportar", command=exportar).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=dialog.destroy).pack(side="left", padx=5)
        
        # Tornar a janela modal
        dialog.transient(self.view.window)
        dialog.grab_set()
        self.view.window.wait_window(dialog)
    
    def excluir_caixa(self):
        """Exclui a caixa selecionada"""
        try:
            selecionado = self.view.tree.selection()
            if not selecionado:
                messagebox.showwarning("Atenção", "Por favor, selecione uma caixa para excluir.")
                return
            
            item = self.view.tree.item(selecionado[0])
            numero_caixa = item['values'][0]
            
            if messagebox.askyesno("Confirmar Exclusão", 
                f"Tem certeza que deseja excluir a caixa {numero_caixa}?\n\n" +
                "⚠️ Esta ação não pode ser desfeita!"):
                
                from app.models.caixa import Caixa
                sucesso, mensagem = Caixa.excluir_caixa(numero_caixa)
                
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem)
                    self.carregar_caixas_fechadas()  # Atualizar a lista
                    
                    # Atualizar a tela de leituras se disponível
                    if self.main_controller and hasattr(self.main_controller, 'atualizar_tela_leituras'):
                        self.main_controller.atualizar_tela_leituras()
                else:
                    messagebox.showerror("Erro", mensagem)
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir caixa:\n{str(e)}")
    
    def excluir_item(self):
        """Exclui o item selecionado da caixa"""
        try:
            if not self.janela_detalhes or not hasattr(self, 'tree_detalhes'):
                messagebox.showwarning("Atenção", "Por favor, abra os detalhes da caixa primeiro.")
                return
            
            selecionado = self.tree_detalhes.selection()
            if not selecionado:
                messagebox.showwarning("Atenção", "Por favor, selecione um item para excluir.")
                return
            
            item = self.tree_detalhes.item(selecionado[0])
            serial = item['values'][0]  # Serial é a primeira coluna
            numero_caixa = self.numero_caixa_atual
            
            if messagebox.askyesno("Confirmar Exclusão", 
                f"Tem certeza que deseja remover o item {serial} da caixa {numero_caixa}?\n\n" +
                "⚠️ Esta ação não pode ser desfeita!"):
                
                from app.models.caixa import Caixa
                sucesso, mensagem = Caixa.excluir_item_caixa(numero_caixa, serial)
                
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem)
                    # Atualizar a visualização
                    self.visualizar_detalhes_caixa(numero_caixa=numero_caixa)
                    self.carregar_caixas_fechadas()
                    
                    # Atualizar a tela de leituras se disponível
                    if self.main_controller:
                        self.main_controller.atualizar_tela_leituras()
                        # Verificar itens sem caixa
                        self.main_controller.verificar_itens_sem_caixa()
                else:
                    messagebox.showerror("Erro", mensagem)
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir item:\n{str(e)}")
    
    def mostrar_menu_contexto_item(self, event):
        """Mostra o menu de contexto para itens na posição do clique"""
        try:
            # Selecionar o item clicado
            item = self.tree_detalhes.identify_row(event.y)
            if item:
                self.tree_detalhes.selection_set(item)
                self.menu_contexto_itens.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contexto_itens.grab_release()
    
    def reabrir_caixa(self):
        """Reabre uma caixa fechada"""
        try:
            selecionado = self.view.tree.selection()
            if not selecionado:
                messagebox.showwarning("Atenção", "Por favor, selecione uma caixa para reabrir.")
                return
            
            item = self.view.tree.item(selecionado[0])
            numero_caixa = item['values'][0]
            
            if messagebox.askyesno("Confirmar Reabertura", 
                f"Tem certeza que deseja reabrir a caixa {numero_caixa}?\n\n" +
                "⚠️ Cada caixa pode ser reaberta no máximo 2 vezes."):
                
                from app.models.caixa import Caixa
                sucesso, mensagem = Caixa.reabrir_caixa(numero_caixa)
                
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem)
                    self.carregar_caixas_fechadas()  # Atualizar a lista
                    
                    # Atualizar a tela de leituras se disponível
                    if self.main_controller:
                        self.main_controller.atualizar_status_caixa()
                        self.main_controller.atualizar_tela_leituras()
                else:
                    messagebox.showerror("Erro", mensagem)
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao reabrir caixa:\n{str(e)}") 