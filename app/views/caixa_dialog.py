import tkinter as tk
from tkinter import ttk

class CaixaDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Abrir Nova Caixa")
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centralizar o diálogo
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Número da caixa
        self.numero_caixa = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Label
        ttk.Label(frame, text="Digite o número da caixa:").pack(pady=(0, 10))
        
        # Entry
        self.entry = ttk.Entry(frame, width=20)
        self.entry.pack(pady=(0, 20))
        self.entry.focus()
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Confirmar", command=self.confirmar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side="right", padx=5)
        
        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self.confirmar())
        
    def confirmar(self):
        numero = self.entry.get().strip()
        if numero:
            self.numero_caixa = numero
            self.dialog.destroy()
        
    def cancelar(self):
        self.dialog.destroy()
        
    def mostrar(self):
        self.dialog.wait_window()
        return self.numero_caixa 