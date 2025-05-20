import tkinter as tk
from tkinter import ttk

class ResumoView:
    def __init__(self, controller, status):
        self.controller = controller
        self.window = tk.Toplevel()
        self.window.title(f"Resumo - Status: {status}")
        self.window.geometry("1200x500")
        self.setup_ui(status)

    def setup_ui(self, status):
        frame_top = tk.Frame(self.window)
        frame_top.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_top, text="Pesquisar:").pack(side="left")
        self.entry_search = tk.Entry(frame_top)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", 
            lambda event: self.controller.filtrar_resumo(self.entry_search.get()))

        tk.Button(frame_top, text="📤 Exportar Excel", 
            command=lambda: self.controller.exportar_resumo(status)
        ).pack(side="left", padx=5)

        # Criar Treeview
        colunas = ("Pedido", "Data Pedido", "Máquina", "Item", "Status", 
                  "Qtd Programada", "Qtd Enviada", "Diferença", "Diferença de Dias")
        
        self.tree = ttk.Treeview(self.window, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)