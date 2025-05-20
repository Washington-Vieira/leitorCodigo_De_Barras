import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import sqlite3
from app.models.database import Database
from tkinter import messagebox
from .codigos_nao_identificados_view import CodigosNaoIdentificadosView

class LoadingDialog:
    def __init__(self, parent, message="Processando..."):
        self.top = tk.Toplevel(parent)
        self.top.title("Importando")
        
        # Centralizar a janela
        window_width = 300
        window_height = 100
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Remover decorações da janela
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)
        
        # Configurar layout
        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_rowconfigure(2, weight=1)
        self.top.grid_columnconfigure(0, weight=1)
        
        # Adicionar mensagem
        self.label = tk.Label(self.top, text=message)
        self.label.grid(row=0, pady=(10, 5))
        
        # Adicionar barra de progresso
        self.progress = ttk.Progressbar(self.top, mode='indeterminate', length=200)
        self.progress.grid(row=1, pady=5)
        self.progress.start(10)
        
        # Forçar foco na janela
        self.top.focus_force()
    
    def update_message(self, message):
        """Atualiza a mensagem do diálogo"""
        self.label.config(text=message)
        self.top.update()
    
    def close(self):
        """Fecha o diálogo de loading"""
        self.top.grab_release()
        self.top.destroy()

class DataSeletorDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Selecionar Data para Relatório")
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
        
        # Data selecionada
        self.data_selecionada = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Label
        ttk.Label(frame, text="Selecione a data para o relatório:").pack(pady=(0, 10))
        
        # Calendário
        self.calendar = DateEntry(frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='dd/mm/yyyy')
        self.calendar.pack(pady=(0, 20))
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Confirmar", command=self.confirmar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side="right", padx=5)
        
    def confirmar(self):
        self.data_selecionada = self.calendar.get_date()
        self.dialog.destroy()
        
    def cancelar(self):
        self.dialog.destroy()
        
    def mostrar(self):
        self.dialog.wait_window()
        return self.data_selecionada

class MainView:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Leitor de Código de Barras")
        self.root.geometry("1400x500")  # Aumentei a largura para acomodar a nova coluna
        
        # Configurar estilos do Treeview
        self.setup_styles()
        
        # Inicializar componentes da interface
        self.setup_ui()
        
        # Iniciar atualização automática
        self.iniciar_atualizacao_automatica()

    def setup_styles(self):
        """Configura os estilos do Treeview e botões"""
        style = ttk.Style()
        
        # Configurar cores para as tags do Treeview
        style.configure("Treeview", rowheight=25)
        style.map("Treeview",
            foreground=[("selected", "#000000")],
            background=[("selected", "#CCE5FF")]
        )
        
        # Configurar cores alternadas para as linhas
        style.configure("Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            selectbackground="#CCE5FF"
        )
        
        # Configurar estilos dos botões
        style.configure("Accent.TButton",
            background="#4CAF50",  # Verde
            foreground="black",    # Texto preto
            padding=5
        )
        
        style.configure("Warning.TButton",
            background="#f44336",  # Vermelho
            foreground="black",    # Texto preto
            padding=5
        )

        # Novo estilo para o botão de itens sem caixa
        style.configure("Alert.TButton",
            background="white",
            foreground="black",
            padding=5,
            borderwidth=2,
            relief="solid"
        )
        style.map("Alert.TButton",
            background=[("active", "#ffe0e0")],  # Vermelho claro quando hover
            bordercolor=[("", "#d32f2f")]  # Contorno vermelho
        )

        # Novo estilo para o botão de caixas fechadas
        style.configure("Info.TButton",
            background="white",
            foreground="black",
            padding=5,
            borderwidth=2,
            relief="solid"
        )
        style.map("Info.TButton",
            background=[("active", "#e3f2fd")],  # Azul claro quando hover
            bordercolor=[("", "#1976d2")]  # Contorno azul
        )

    def setup_ui(self):
        """Configura a interface do usuário"""
        self.create_top_frame()
        self.create_treeview()
        self.setup_context_menu()
        self.criar_menu()

    def atualizar_tabela(self):
        """Atualiza os dados da tabela principal"""
        if hasattr(self, 'controller') and hasattr(self, 'tree'):
            self.controller.carregar_dados_iniciais()

    def create_top_frame(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root)  # Salvar referência
        self.main_frame.pack(pady=5, fill="x")
        
        # Frame superior para caixa
        caixa_frame = ttk.Frame(self.main_frame)
        caixa_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Frame de status da caixa (com borda e padding)
        status_frame = ttk.Frame(caixa_frame, relief="solid", borderwidth=1)
        status_frame.pack(side="left", padx=5, pady=5, ipadx=10, ipady=5)
        
        # Ícone de status
        self.label_icone = ttk.Label(status_frame, text="🔒", font=("Arial", 16))
        self.label_icone.pack(side="left", padx=(5,0))
        
        # Label de status da caixa
        self.label_caixa = ttk.Label(status_frame, 
            text="Nenhuma caixa aberta", 
            font=("Arial", 10, "bold"),
            foreground="gray"
        )
        self.label_caixa.pack(side="left", padx=5)
        
        # Label de contagem
        self.label_contagem = ttk.Label(status_frame, 
            text="", 
            font=("Arial", 9),
            foreground="gray"
        )
        self.label_contagem.pack(side="left", padx=5)
        
        # Frame para botões de caixa
        botoes_frame = ttk.Frame(caixa_frame)
        botoes_frame.pack(side="left", padx=5)
        
        # Botões de caixa com ícones maiores
        ttk.Button(botoes_frame, 
            text="📦 Abrir Caixa",
            command=self.controller.abrir_caixa,
            style="Accent.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(botoes_frame, 
            text="🔒 Fechar Caixa",
            command=self.controller.fechar_caixa,
            style="Warning.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(botoes_frame,
            text="📋 Caixas Fechadas",
            command=self.controller.abrir_caixas_fechadas,
            style="Info.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(botoes_frame,
            text="❗ Itens Sem Caixa",
            command=self.controller.mostrar_itens_sem_caixa,
            style="Alert.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(botoes_frame,
            text="⚠️ Códigos Não Identificados",
            command=self.controller.mostrar_codigos_nao_identificados,
            style="Alert.TButton"
        ).pack(side="left", padx=5)
        
        # Frame inferior para código de barras e outros botões
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill="x", padx=5)

        label = ttk.Label(bottom_frame, text="Escaneie o código de barras:")
        label.pack(side="left")

        self.entry_codigo = ttk.Entry(bottom_frame, font=("Arial", 14), width=40)
        self.entry_codigo.pack(side="left", padx=10)
        self.entry_codigo.focus()
        self.entry_codigo.bind("<Return>", self.controller.verificar_codigo)

        botoes = [
            ("📥 Importar", self.controller.importar_planilha),
            ("🔄 Atualizar", self.controller.atualizar_dados),
            ("📋 Pendentes", self.controller.abrir_resumo_pendentes),
            ("🔄 Em Andamento", self.controller.abrir_resumo_andamento),
            ("✅ Concluídos", self.controller.abrir_resumo_concluidos),
            ("📊 Controladoria", self.solicitar_data_controladoria),
            ("📤 Exportar", self.controller.exportar_excel)
        ]

        for texto, comando in botoes:
            ttk.Button(bottom_frame, text=texto, command=comando).pack(side="left", padx=5)

    def solicitar_data_controladoria(self):
        """Abre o diálogo de seleção de data e chama o controlador com a data selecionada"""
        seletor = DataSeletorDialog(self.root)
        data_selecionada = seletor.mostrar()
        if data_selecionada:
            self.controller.exportar_controladoria(data_selecionada)

    def create_treeview(self):
        colunas = ("Pedido", "Data Pedido", "Serial", "Item", "Máquina", "Linha", 
                   "Qtd Programada", "Qtd Enviada", "Status", "Data/Hora Leitura", 
                   "Diferença de Dias", "Caixa")
        
        # Larguras personalizadas para cada coluna
        larguras = {
            "Pedido": 120,
            "Data Pedido": 100,
            "Serial": 150,
            "Item": 200,
            "Máquina": 100,
            "Linha": 80,
            "Qtd Programada": 100,
            "Qtd Enviada": 100,
            "Status": 100,
            "Data/Hora Leitura": 150,
            "Diferença de Dias": 100,
            "Caixa": 300  # Aumentei a largura para acomodar mais informações
        }
        
        self.tree = ttk.Treeview(self.root, columns=colunas, show="headings")
        
        # Configurar cada coluna com largura e tooltip
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=larguras[col], anchor="center")
            
            # Adicionar tooltip no cabeçalho
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_coluna(c))
        
        # Configurar tags para colorização
        self.tree.tag_configure("aberta", background="#E8F5E9")  # Verde claro para caixas abertas
        self.tree.tag_configure("fechada", background="#FFEBEE")  # Vermelho claro para caixas fechadas
        self.tree.tag_configure("odd", background="#F5F5F5")  # Cinza claro para linhas ímpares
        self.tree.tag_configure("duplicado",  # Tag para itens duplicados
            background="#FFE0E0",  # Vermelho claro
            foreground="#FF0000"   # Vermelho
        )
        
        self.tree.pack(pady=10, fill="both", expand=True)

        # Adicionar bindings para o menu de contexto e tooltips
        self.tree.bind("<Button-3>", self.show_context_menu)  # Botão direito
        self.tree.bind("<Delete>", self.controller.remover_leitura)  # Tecla Delete
        self.tree.bind("<Motion>", self.mostrar_tooltip)  # Movimento do mouse

    def ordenar_coluna(self, coluna):
        """Ordena a tabela pela coluna clicada"""
        # Obter todos os itens da tabela
        itens = [(self.tree.set(item, coluna), item) for item in self.tree.get_children("")]
        
        # Inverter a ordem se já estiver ordenado
        if hasattr(self, "_ultima_coluna") and self._ultima_coluna == coluna:
            itens.reverse()
            self._ultima_coluna = None
        else:
            # Ordenar considerando números e datas
            try:
                # Tentar ordenar como números
                itens.sort(key=lambda x: float(x[0]) if x[0] != "-" else float("-inf"))
            except ValueError:
                try:
                    # Tentar ordenar como datas
                    itens.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%Y %H:%M:%S") if x[0] != "-" else datetime.min)
                except ValueError:
                    # Ordenar como texto
                    itens.sort()
            self._ultima_coluna = coluna
        
        # Reordenar a tabela
        for index, (_, item) in enumerate(itens):
            self.tree.move(item, "", index)
        
        # Reconfigurar cores das linhas
        self.configurar_cores_linhas()

    def mostrar_tooltip(self, event):
        """Mostra tooltip com o conteúdo completo da célula"""
        # Identificar a célula sob o cursor
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        coluna = self.tree.identify_column(event.x)
        if not coluna:
            return
        
        # Obter o índice da coluna (remove o #)
        col_num = int(coluna[1]) - 1
        
        # Obter o valor da célula
        valor = self.tree.item(item)["values"][col_num]
        
        # Criar tooltip se o valor for muito longo
        if len(str(valor)) > 20:
            self.mostrar_tooltip_texto(event, str(valor))
        else:
            self.esconder_tooltip()

    def mostrar_tooltip_texto(self, event, texto):
        """Mostra um tooltip com o texto fornecido"""
        # Criar tooltip se não existir
        if not hasattr(self, "tooltip"):
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip_label = tk.Label(
                self.tooltip,
                text="",
                justify="left",
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                font=("Arial", "8", "normal")
            )
            self.tooltip_label.pack(ipadx=1)
        
        # Atualizar texto e posição
        self.tooltip_label.config(text=texto)
        self.tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        self.tooltip.deiconify()

    def esconder_tooltip(self):
        """Esconde o tooltip se existir"""
        if hasattr(self, "tooltip"):
            self.tooltip.withdraw()

    def setup_context_menu(self):
        """Configura o menu de contexto para a tabela"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="🗑️ Remover Leitura",
            command=self.controller.remover_leitura
        )

    def show_context_menu(self, event):
        """Mostra o menu de contexto na posição do clique"""
        # Primeiro, seleciona o item sob o cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def atualizar_status_caixa(self, numero_caixa):
        """Atualiza o status visual da caixa"""
        if numero_caixa:
            # Buscar informações da caixa
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            # Buscar status e horários da caixa
            cursor.execute('''
                SELECT status, data_fechamento, hora_fechamento, total_itens
                FROM caixas 
                WHERE numero_caixa = ?
            ''', (numero_caixa,))
            info_caixa = cursor.fetchone()
            
            if info_caixa:
                status, data_fechamento, hora_fechamento, total_itens = info_caixa
                
                if status == "ABERTA":
                    # Contar itens atuais para caixa aberta
                    cursor.execute('''
                        SELECT COUNT(*) FROM leituras 
                        WHERE numero_caixa = ? AND status_caixa = "ABERTA"
                    ''', (numero_caixa,))
                    total_itens = cursor.fetchone()[0]
                    
                    # Atualizar visual para caixa aberta
                    self.label_icone.config(text="📦")
                    self.label_caixa.config(
                        text=f"Caixa {numero_caixa} aberta",
                        foreground="#4CAF50"  # Verde
                    )
                    self.label_contagem.config(
                        text=f"({total_itens} itens)",
                        foreground="#4CAF50"
                    )
                else:
                    # Formatar data e hora de fechamento
                    data_formatada = datetime.strptime(data_fechamento, '%Y-%m-%d').strftime('%d/%m/%Y')
                    
                    # Atualizar visual para caixa fechada
                    self.label_icone.config(text="🔒")
                    self.label_caixa.config(
                        text=f"Caixa {numero_caixa} fechada",
                        foreground="gray"
                    )
                    self.label_contagem.config(
                        text=f"({total_itens} itens - Fechada em {data_formatada} às {hora_fechamento})",
                        foreground="gray"
                    )
            
            conn.close()
        else:
            # Atualizar para estado sem caixa
            self.label_icone.config(text="🔒")
            self.label_caixa.config(
                text="Nenhuma caixa aberta",
                foreground="gray"
            )
            self.label_contagem.config(text="")
            
            # Remover aviso se existir
            if hasattr(self, 'label_aviso'):
                self.label_aviso.pack_forget()

    def configurar_cores_linhas(self):
        """Configura as cores das linhas do Treeview"""
        for i, item in enumerate(self.tree.get_children()):
            # Pegar as tags existentes
            tags = list(self.tree.item(item)["tags"])
            
            # Adicionar tag para linhas ímpares
            if i % 2 == 1 and "odd" not in tags:
                tags.append("odd")
            
            # Atualizar as tags do item
            self.tree.item(item, tags=tags)

    def iniciar_atualizacao_automatica(self):
        """Inicia a atualização automática do status da caixa"""
        self.atualizar_status_periodico()

    def atualizar_status_periodico(self):
        """Atualiza o status da caixa periodicamente"""
        # Atualizar status atual
        self.controller.atualizar_status_caixa()
        
        # Agendar próxima atualização (a cada 30 segundos)
        self.root.after(30000, self.atualizar_status_periodico)

    def criar_menu(self):
        """Cria o menu principal da aplicação"""
        menubar = tk.Menu(self.root)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menu_arquivo.add_command(label="📦 Abrir Caixa", command=self.controller.abrir_caixa)
        menu_arquivo.add_command(label="📋 Caixas Fechadas", command=self.controller.abrir_caixas_fechadas)
        menu_arquivo.add_command(label="❗ Itens Sem Caixa", command=self.controller.mostrar_itens_sem_caixa)
        menu_arquivo.add_command(label="⚠️ Códigos Não Identificados", command=self.controller.mostrar_codigos_nao_identificados)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="❌ Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)

    def mostrar_codigos_nao_identificados(self):
        """Abre a janela de códigos não identificados"""
        CodigosNaoIdentificadosView(self.root)