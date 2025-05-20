import tkinter as tk
from tkinter import ttk
import sqlite3
from app.models.database import Database

class SelecionarCaixaDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Selecionar Caixa")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centralizar o diálogo
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Caixa selecionada
        self.caixa_selecionada = None
        
        self.setup_ui()
        self.carregar_caixas()
        
    def setup_ui(self):
        # Frame principal
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Label
        ttk.Label(frame, text="Selecione uma caixa aberta:", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        # Frame para a tabela
        frame_tabela = ttk.Frame(frame)
        frame_tabela.pack(fill="both", expand=True, pady=(0, 10))
        
        # Criar Treeview
        colunas = ("numero_caixa", "total_itens", "data_abertura", "hora_abertura")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=8)
        
        # Configurar cabeçalhos
        headers = {
            "numero_caixa": "Número da Caixa",
            "total_itens": "Total de Itens",
            "data_abertura": "Data de Abertura",
            "hora_abertura": "Hora de Abertura"
        }
        
        larguras = {
            "numero_caixa": 120,
            "total_itens": 100,
            "data_abertura": 120,
            "hora_abertura": 120
        }
        
        for col in colunas:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=larguras[col])
        
        # Scrollbars
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
        
        # Binding para duplo clique
        self.tree.bind("<Double-1>", lambda e: self.confirmar())
        
        # Botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            frame_botoes,
            text="Confirmar",
            command=self.confirmar
        ).pack(side="left", padx=5)
        
        ttk.Button(
            frame_botoes,
            text="Cancelar",
            command=self.cancelar
        ).pack(side="right", padx=5)
    
    def carregar_caixas(self):
        """Carrega todas as caixas abertas"""
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            # Consulta corrigida para mostrar caixas abertas
            cursor.execute('''
                SELECT 
                    c.numero_caixa,
                    (
                        SELECT COUNT(*)
                        FROM leituras l2
                        WHERE l2.numero_caixa = c.numero_caixa
                        AND l2.status_caixa = 'ABERTA'
                    ) as total_itens,
                    strftime('%Y-%m-%d', c.data_abertura) as data_abertura,
                    c.hora_abertura
                FROM caixas c
                WHERE c.status = 'ABERTA'
                ORDER BY c.data_abertura DESC, c.hora_abertura DESC
            ''')
            
            # Limpar tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Adicionar caixas
            for caixa in cursor.fetchall():
                try:
                    # Formatar a data para dd/mm/yyyy
                    data = caixa[2].split('-')
                    data_formatada = f"{data[2]}/{data[1]}/{data[0]}"
                except:
                    data_formatada = caixa[2]  # Usar data original se não conseguir formatar
                
                self.tree.insert("", "end", values=(
                    caixa[0],  # número da caixa
                    caixa[1] or 0,  # total de itens (0 se for None)
                    data_formatada,  # data formatada
                    caixa[3]   # hora
                ))
            
            conn.close()
            
            # Se não houver caixas abertas, mostrar mensagem
            if not self.tree.get_children():
                ttk.Label(
                    self.dialog,
                    text="Não há caixas abertas disponíveis!",
                    font=("Arial", 10),
                    foreground="red"
                ).pack(pady=10)
                
                # Desabilitar botão de confirmar
                for child in self.dialog.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Frame):
                                for btn in subchild.winfo_children():
                                    if isinstance(btn, ttk.Button) and btn['text'] == "Confirmar":
                                        btn.state(['disabled'])
            
        except Exception as e:
            print(f"Erro ao carregar caixas: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def confirmar(self):
        """Confirma a seleção da caixa"""
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado[0])
            self.caixa_selecionada = item['values'][0]  # Número da caixa
            self.dialog.destroy()
        
    def cancelar(self):
        """Cancela a seleção"""
        self.dialog.destroy()
    
    def mostrar(self):
        """Mostra o diálogo e retorna a caixa selecionada"""
        self.dialog.wait_window()
        return self.caixa_selecionada 