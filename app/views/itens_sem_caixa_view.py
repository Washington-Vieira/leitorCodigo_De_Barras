import tkinter as tk
from tkinter import ttk

class ItensSemCaixaView:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Toplevel()
        self.window.title("Itens Sem Caixa")
        self.window.geometry("1200x600")
        
        # Configurar grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Frame superior para botões e informações
        self.frame_superior = ttk.Frame(self.window)
        self.frame_superior.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Frame para botões (esquerda)
        self.frame_botoes = ttk.Frame(self.frame_superior)
        self.frame_botoes.pack(side="left", fill="x")
        
        # Botão para atribuir caixa
        self.btn_atribuir = ttk.Button(
            self.frame_botoes,
            text="Atribuir à Caixa",
            command=self.controller.solicitar_numero_caixa
        )
        self.btn_atribuir.pack(side="left", padx=5)
        
        # Botão para atualizar
        self.btn_atualizar = ttk.Button(
            self.frame_botoes,
            text="Atualizar Lista",
            command=self.controller.atualizar_dados
        )
        self.btn_atualizar.pack(side="left", padx=5)
        
        # Botão para excluir
        self.btn_excluir = ttk.Button(
            self.frame_botoes,
            text="🗑️ Excluir Item",
            command=self.controller.remover_item
        )
        self.btn_excluir.pack(side="left", padx=5)
        
        # Label com total de itens (direita)
        self.label_total = ttk.Label(
            self.frame_superior,
            text="Total: 0 itens",
            font=("Arial", 10, "bold")
        )
        self.label_total.pack(side="right", padx=5)
        
        # Frame para a tabela
        self.frame_tabela = ttk.Frame(self.window)
        self.frame_tabela.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configurar Treeview
        self.tree = ttk.Treeview(
            self.frame_tabela,
            columns=(
                "serial", "pedido", "item", "maquina", "linha",
                "quantidade", "data", "hora", "status"
            ),
            show="headings"
        )
        
        # Configurar colunas
        self.tree.heading("serial", text="Serial")
        self.tree.heading("pedido", text="Pedido")
        self.tree.heading("item", text="Item")
        self.tree.heading("maquina", text="Máquina")
        self.tree.heading("linha", text="Linha")
        self.tree.heading("quantidade", text="Quantidade")
        self.tree.heading("data", text="Data")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("status", text="Status")
        
        # Configurar larguras das colunas
        self.tree.column("serial", width=150)
        self.tree.column("pedido", width=100)
        self.tree.column("item", width=200)
        self.tree.column("maquina", width=100)
        self.tree.column("linha", width=80)
        self.tree.column("quantidade", width=100)
        self.tree.column("data", width=100)
        self.tree.column("hora", width=100)
        self.tree.column("status", width=100)
        
        # Configurar cores para as tags
        self.tree.tag_configure("sem_caixa", background="#fff3e0")  # Laranja claro
        self.tree.tag_configure("pendente", background="#e8f5e9")   # Verde claro
        
        # Adicionar scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.frame_tabela,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Configurar seleção múltipla
        self.tree.configure(selectmode="extended")
        
        # Criar menu de contexto
        self.menu_contexto = tk.Menu(self.window, tearoff=0)
        self.menu_contexto.add_command(
            label="Atribuir à Caixa",
            command=self.controller.solicitar_numero_caixa
        )
        self.menu_contexto.add_command(
            label="🗑️ Excluir Item",
            command=self.controller.remover_item
        )
        
        # Bind de teclas e eventos
        self.window.bind("<Control-a>", self.selecionar_todos)
        self.window.bind("<Delete>", self.controller.remover_item)
        self.tree.bind("<Double-1>", lambda e: self.controller.solicitar_numero_caixa())
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)
        
        # Carregar dados iniciais
        self.controller.atualizar_dados()
        
        # Protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.ao_fechar)
        
        # Centralizar a janela
        self.centralizar_janela()
    
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def atualizar_titulo(self, total_itens):
        """Atualiza o título da janela e o label com o total de itens"""
        self.window.title(f"Itens Sem Caixa - {total_itens} item{'s' if total_itens != 1 else ''}")
        self.label_total.config(
            text=f"Total: {total_itens} item{'s' if total_itens != 1 else ''}",
            foreground="#d32f2f" if total_itens > 0 else "#4caf50"
        )
    
    def selecionar_todos(self, event=None):
        """Seleciona todos os itens da tabela"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def mostrar_menu_contexto(self, event):
        """Mostra o menu de contexto na posição do clique"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu_contexto.tk_popup(event.x_root, event.y_root)
    
    def ao_fechar(self):
        """Ação ao fechar a janela"""
        self.window.withdraw()  # Apenas esconde a janela ao invés de destruí-la 