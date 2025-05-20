import tkinter as tk
from tkinter import ttk
from datetime import datetime

class CaixasFechadasView:
    def __init__(self, controller):
        """Inicializa a view de caixas fechadas"""
        self.controller = controller
        
        # Criar janela principal
        self.window = tk.Toplevel()
        self.window.title("Caixas Fechadas")
        self.window.geometry("1200x600")
        
        # Centralizar a janela
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configurar o grid
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Frame superior para filtros
        self.criar_frame_filtros()
        
        # Criar Treeview
        self.criar_treeview()
        
        # Frame inferior para botões
        self.criar_frame_botoes()
        
        # Criar menu de contexto
        self.criar_menu_contexto()
        
        # Configurar protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        
        # Forçar foco na janela
        self.window.focus_force()
        
        # Carregar dados iniciais
        self.controller.carregar_caixas_fechadas()
    
    def criar_frame_filtros(self):
        frame_filtros = ttk.Frame(self.window, padding="10")
        frame_filtros.grid(row=0, column=0, sticky="ew")
        
        # Label e campo de pesquisa
        ttk.Label(frame_filtros, text="Pesquisar:").pack(side="left", padx=(0, 5))
        self.entry_pesquisa = ttk.Entry(frame_filtros, width=30)
        self.entry_pesquisa.pack(side="left", padx=5)
        self.entry_pesquisa.bind("<KeyRelease>", self.controller.filtrar_caixas)
        
        # Filtro de data
        ttk.Label(frame_filtros, text="Data:").pack(side="left", padx=(20, 5))
        self.combo_data = ttk.Combobox(frame_filtros, values=["Todas", "Hoje", "Última semana", "Último mês"])
        self.combo_data.set("Todas")
        self.combo_data.pack(side="left", padx=5)
        self.combo_data.bind("<<ComboboxSelected>>", self.controller.filtrar_caixas)
    
    def criar_treeview(self):
        # Frame para a tabela
        frame_tabela = ttk.Frame(self.window, padding="10")
        frame_tabela.grid(row=1, column=0, sticky="nsew")
        
        # Configurar colunas
        colunas = (
            "numero_caixa", "total_itens", "data_fechamento", 
            "hora_fechamento", "usuario_fechamento"
        )
        
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        
        # Configurar cabeçalhos
        headers = {
            "numero_caixa": "Número da Caixa",
            "total_itens": "Total de Itens",
            "data_fechamento": "Data de Fechamento",
            "hora_fechamento": "Hora de Fechamento",
            "usuario_fechamento": "Fechado por"
        }
        
        for col in colunas:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=200)
        
        # Adicionar scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Configurar expansão
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)
        
        # Bindings
        self.tree.bind("<Double-1>", self.controller.visualizar_detalhes_caixa)
        self.tree.bind("<Delete>", lambda e: self.controller.excluir_caixa())
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)
    
    def criar_frame_botoes(self):
        frame_botoes = ttk.Frame(self.window, padding="10")
        frame_botoes.grid(row=2, column=0, sticky="ew")
        
        ttk.Button(
            frame_botoes, 
            text="📋 Exportar Relatório",
            command=self.controller.exportar_relatorio
        ).pack(side="left", padx=5)
        
        ttk.Button(
            frame_botoes,
            text="📅 Exportar por Período",
            command=self.controller.exportar_por_periodo
        ).pack(side="left", padx=5)
        
        ttk.Button(
            frame_botoes, 
            text="🔍 Visualizar Detalhes",
            command=self.controller.visualizar_detalhes_caixa
        ).pack(side="left", padx=5)
        
        ttk.Button(
            frame_botoes,
            text="🗑️ Excluir Caixa",
            command=self.controller.excluir_caixa
        ).pack(side="left", padx=5)
        
        ttk.Button(
            frame_botoes, 
            text="❌ Fechar",
            command=self.fechar_janela
        ).pack(side="right", padx=5)
    
    def criar_menu_contexto(self):
        """Cria o menu de contexto para a tabela"""
        self.menu_contexto = tk.Menu(self.window, tearoff=0)
        self.menu_contexto.add_command(
            label="🔍 Visualizar Detalhes",
            command=self.controller.visualizar_detalhes_caixa
        )
        self.menu_contexto.add_command(
            label="🔓 Reabrir Caixa",
            command=self.controller.reabrir_caixa
        )
        self.menu_contexto.add_command(
            label="🗑️ Excluir Caixa",
            command=self.controller.excluir_caixa
        )
    
    def mostrar_menu_contexto(self, event):
        """Mostra o menu de contexto na posição do clique"""
        try:
            # Selecionar o item clicado
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self.menu_contexto.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contexto.grab_release()
    
    def adicionar_caixa(self, caixa):
        """Adiciona uma caixa à tabela"""
        # Formatar a data para dd/mm/yyyy
        data_formatada = datetime.strptime(caixa['data_fechamento'], '%Y-%m-%d').strftime('%d/%m/%Y')
        
        self.tree.insert("", "end", values=(
            caixa['numero_caixa'],
            caixa['total_itens'],
            data_formatada,
            caixa['hora_fechamento'],
            caixa['usuario_fechamento'] if 'usuario_fechamento' in caixa else 'Sistema'
        ))
    
    def limpar_tabela(self):
        """Limpa todas as linhas da tabela"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def atualizar_titulo(self, total_caixas):
        """Atualiza o título da janela com o total de caixas"""
        self.window.title(f"Caixas Fechadas - Total: {total_caixas} caixa{'s' if total_caixas != 1 else ''}")
        
        # Atualizar label de total se existir
        if hasattr(self, 'label_total'):
            self.label_total.config(text=f"Total: {total_caixas} caixa{'s' if total_caixas != 1 else ''}")
        else:
            self.label_total = ttk.Label(self.window, 
                text=f"Total: {total_caixas} caixa{'s' if total_caixas != 1 else ''}", 
                font=("Arial", 10, "bold"))
            self.label_total.grid(row=3, column=0, sticky="w", padx=10, pady=5)
    
    def fechar_janela(self):
        """Fecha a janela e limpa a referência no controller"""
        self.window.destroy()
        self.controller.view = None 