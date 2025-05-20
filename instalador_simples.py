import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import winreg
import ctypes
from datetime import datetime

class InstaladorSimples:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instalador - Leitor de Código de Barras")
        self.root.geometry("700x500")
        
        # Centralizar janela
        window_width = 700
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Variáveis
        self.diretorio_instalacao = tk.StringVar(value=os.path.expanduser("~/LeitorCodigoBarras"))
        self.criar_atalho_desktop = tk.BooleanVar(value=True)
        self.criar_atalho_menu = tk.BooleanVar(value=True)
        self.passo_atual = 1
        self.total_passos = 3
        
        # Criar frames principais
        self.main_container = None
        self.progress_frame = None
        self.step_container = None
        self.button_frame = None
        self.frame_passo1 = None
        self.frame_passo2 = None
        self.frame_passo3 = None
        
        # Criar botões de navegação
        self.btn_anterior = None
        self.btn_proximo = None
        self.btn_instalar = None
        self.btn_cancelar = None
        
        # Inicializar interface
        self.setup_ui()
    
    def setup_ui(self):
        # Estilo
        style = ttk.Style()
        style.configure("Custom.TButton", padding=10)
        style.configure("Custom.TLabel", padding=5)
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("Step.TLabel", font=("Arial", 10))
        
        # Container principal
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header = ttk.Label(
            self.main_container,
            text="Instalação do Sistema de Leitura de Códigos de Barras",
            style="Header.TLabel"
        )
        header.pack(pady=20)
        
        # Indicador de progresso
        self.progress_frame = ttk.Frame(self.main_container)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = ttk.Label(
            self.progress_frame,
            text=f"Passo {self.passo_atual} de {self.total_passos}",
            style="Step.TLabel"
        )
        self.progress_label.pack()
        
        self.progress = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=600
        )
        self.progress.pack(pady=10)
        
        # Container para os passos
        self.step_container = ttk.Frame(self.main_container)
        self.step_container.pack(fill=tk.BOTH, expand=True)
        
        # Botões de navegação
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.pack(pady=20)
        
        self.btn_anterior = ttk.Button(
            self.button_frame,
            text="← Anterior",
            command=self.passo_anterior,
            style="Custom.TButton"
        )
        
        self.btn_proximo = ttk.Button(
            self.button_frame,
            text="Próximo →",
            command=self.proximo_passo,
            style="Custom.TButton"
        )
        
        self.btn_instalar = ttk.Button(
            self.button_frame,
            text="Instalar",
            command=self.instalar,
            style="Custom.TButton"
        )
        
        self.btn_cancelar = ttk.Button(
            self.button_frame,
            text="Cancelar",
            command=self.root.quit,
            style="Custom.TButton"
        )
        
        # Criar frames para cada passo
        self.criar_passo1()
        self.criar_passo2()
        self.criar_passo3()
        
        # Mostrar primeiro passo e atualizar botões
        self.mostrar_passo(1)
    
    def criar_passo1(self):
        self.frame_passo1 = ttk.Frame(self.step_container)
        
        ttk.Label(
            self.frame_passo1,
            text="Passo 1: Selecione o local de instalação",
            style="Header.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.frame_passo1,
            text="Escolha onde o sistema será instalado:",
            style="Step.TLabel"
        ).pack(pady=5)
        
        dir_frame = ttk.Frame(self.frame_passo1)
        dir_frame.pack(fill=tk.X, pady=10)
        
        self.entry_dir = ttk.Entry(
            dir_frame,
            textvariable=self.diretorio_instalacao,
            width=50
        )
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            dir_frame,
            text="Procurar...",
            command=self.escolher_diretorio
        ).pack(side=tk.LEFT, padx=5)
    
    def criar_passo2(self):
        self.frame_passo2 = ttk.Frame(self.step_container)
        
        ttk.Label(
            self.frame_passo2,
            text="Passo 2: Opções de instalação",
            style="Header.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.frame_passo2,
            text="Selecione as opções desejadas:",
            style="Step.TLabel"
        ).pack(pady=5)
        
        ttk.Checkbutton(
            self.frame_passo2,
            text="Criar atalho na área de trabalho",
            variable=self.criar_atalho_desktop
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(
            self.frame_passo2,
            text="Criar atalho no menu iniciar",
            variable=self.criar_atalho_menu
        ).pack(anchor=tk.W, pady=5)
    
    def criar_passo3(self):
        self.frame_passo3 = ttk.Frame(self.step_container)
        
        ttk.Label(
            self.frame_passo3,
            text="Passo 3: Confirmação",
            style="Header.TLabel"
        ).pack(pady=10)
        
        ttk.Label(
            self.frame_passo3,
            text="Revise as configurações abaixo e clique em 'Instalar' para começar:",
            style="Step.TLabel"
        ).pack(pady=5)
        
        self.resumo_text = tk.Text(self.frame_passo3, height=8, width=60)
        self.resumo_text.pack(pady=10)
        self.resumo_text.config(state='disabled')
    
    def mostrar_passo(self, passo):
        # Esconder todos os frames
        for widget in self.step_container.winfo_children():
            widget.pack_forget()
        
        # Mostrar frame do passo atual
        if passo == 1:
            self.frame_passo1.pack(fill=tk.BOTH, expand=True)
        elif passo == 2:
            self.frame_passo2.pack(fill=tk.BOTH, expand=True)
        elif passo == 3:
            self.atualizar_resumo()
            self.frame_passo3.pack(fill=tk.BOTH, expand=True)
        
        # Atualizar progresso
        self.progress['value'] = (passo / self.total_passos) * 100
        self.progress_label['text'] = f"Passo {passo} de {self.total_passos}"
        
        self.passo_atual = passo
        self.atualizar_botoes()
    
    def atualizar_botoes(self):
        # Remover botões existentes
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()
        
        # Adicionar botões apropriados
        if self.passo_atual > 1:
            self.btn_anterior.pack(side=tk.LEFT, padx=5)
        
        if self.passo_atual < self.total_passos:
            self.btn_proximo.pack(side=tk.LEFT, padx=5)
        else:
            self.btn_instalar.pack(side=tk.LEFT, padx=5)
        
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def atualizar_resumo(self):
        self.resumo_text.config(state='normal')
        self.resumo_text.delete(1.0, tk.END)
        
        resumo = f"""Local de instalação:
{self.diretorio_instalacao.get()}

Atalhos:
• Área de trabalho: {'Sim' if self.criar_atalho_desktop.get() else 'Não'}
• Menu Iniciar: {'Sim' if self.criar_atalho_menu.get() else 'Não'}

Clique em 'Instalar' para iniciar a instalação."""
        
        self.resumo_text.insert(1.0, resumo)
        self.resumo_text.config(state='disabled')
    
    def proximo_passo(self):
        if self.passo_atual < self.total_passos:
            self.mostrar_passo(self.passo_atual + 1)
    
    def passo_anterior(self):
        if self.passo_atual > 1:
            self.mostrar_passo(self.passo_atual - 1)
    
    def escolher_diretorio(self):
        from tkinter import filedialog
        diretorio = filedialog.askdirectory(
            initialdir=self.diretorio_instalacao.get()
        )
        if diretorio:
            self.diretorio_instalacao.set(diretorio)
    
    def instalar(self):
        try:
            diretorio = self.diretorio_instalacao.get()
            
            # Criar diretórios
            self.progress['value'] = 10
            self.progress_label['text'] = "Criando diretórios..."
            os.makedirs(diretorio, exist_ok=True)
            
            # Copiar arquivos
            self.progress['value'] = 30
            self.progress_label['text'] = "Copiando arquivos..."
            dist_dir = "./dist"
            for item in os.listdir(dist_dir):
                s = os.path.join(dist_dir, item)
                d = os.path.join(diretorio, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            
            # Criar diretórios de dados
            self.progress['value'] = 50
            self.progress_label['text'] = "Configurando diretórios de dados..."
            diretorios = ['data/excel_importados', 'data/relatorios', 'data/backup', 'logs']
            for pasta in diretorios:
                os.makedirs(os.path.join(diretorio, pasta), exist_ok=True)
            
            # Inicializar banco de dados
            self.progress['value'] = 70
            self.progress_label['text'] = "Inicializando banco de dados..."
            exe_path = os.path.join(diretorio, "LeitorCodigoBarras.exe")
            os.system(f'"{exe_path}" --init-db')
            
            # Criar atalhos
            self.progress['value'] = 90
            self.progress_label['text'] = "Criando atalhos..."
            if self.criar_atalho_desktop.get() or self.criar_atalho_menu.get():
                self.criar_atalhos()
            
            # Finalizar
            self.progress['value'] = 100
            self.progress_label['text'] = "Instalação concluída!"
            
            messagebox.showinfo(
                "Instalação Concluída",
                "O sistema foi instalado com sucesso!\n\n" +
                "Você pode iniciar o programa através dos atalhos criados."
            )
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Ocorreu um erro durante a instalação:\n{str(e)}"
            )
            self.root.quit()
    
    def criar_atalhos(self):
        exe_path = os.path.join(self.diretorio_instalacao.get(), "LeitorCodigoBarras.exe")
        
        if self.criar_atalho_desktop.get():
            desktop = os.path.expanduser("~/Desktop")
            self.criar_atalho(
                exe_path,
                os.path.join(desktop, "Leitor de Código de Barras.lnk")
            )
        
        if self.criar_atalho_menu.get():
            start_menu = os.path.join(
                os.environ.get("APPDATA"),
                "Microsoft/Windows/Start Menu/Programs"
            )
            os.makedirs(
                os.path.join(start_menu, "Leitor de Código de Barras"),
                exist_ok=True
            )
            self.criar_atalho(
                exe_path,
                os.path.join(
                    start_menu,
                    "Leitor de Código de Barras",
                    "Leitor de Código de Barras.lnk"
                )
            )
    
    def criar_atalho(self, origem, destino):
        try:
            import pythoncom
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(destino)
            shortcut.Targetpath = origem
            shortcut.WorkingDirectory = os.path.dirname(origem)
            shortcut.IconLocation = origem
            shortcut.save()
        except Exception as e:
            print(f"Erro ao criar atalho: {e}")
            # Fallback: criar arquivo .bat
            with open(destino.replace(".lnk", ".bat"), "w") as f:
                f.write(f'@echo off\nstart "" "{origem}"')

if __name__ == "__main__":
    instalador = InstaladorSimples()
    instalador.root.mainloop() 