import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from ..controllers.codigos_nao_identificados_controller import CodigosNaoIdentificadosController

class CodigosNaoIdentificadosView:
    def __init__(self, parent, main_controller=None):
        self.controller = CodigosNaoIdentificadosController()
        self.controller.set_view(self)
        if main_controller:
            self.controller.set_main_controller(main_controller)

        self.window = tk.Toplevel(parent)
        self.window.title("Códigos Não Identificados")
        self.window.geometry("1200x600")
        
        # Configurar grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Frame superior para filtros e ações
        self.frame_superior = ttk.Frame(self.window, padding="5")
        self.frame_superior.grid(row=0, column=0, sticky="ew")
        
        # Frame para botões (esquerda)
        self.frame_botoes = ttk.Frame(self.frame_superior)
        self.frame_botoes.pack(side=tk.LEFT, fill="x")
        
        # Botão de atualizar
        self.btn_atualizar = ttk.Button(
            self.frame_botoes,
            text="🔄 Atualizar",
            command=self.atualizar_lista,
            style="Accent.TButton"
        )
        self.btn_atualizar.pack(side=tk.LEFT, padx=5)
        
        # Botão de atribuir caixa
        self.btn_atribuir_caixa = ttk.Button(
            self.frame_botoes,
            text="📦 Atribuir Caixa",
            command=self.atribuir_caixa,
            style="Info.TButton"
        )
        self.btn_atribuir_caixa.pack(side=tk.LEFT, padx=5)
        
        # Botão para excluir em massa
        self.btn_excluir_massa = ttk.Button(
            self.frame_botoes,
            text="🗑️ Excluir Selecionados",
            command=self.excluir_em_massa,
            style="Warning.TButton"
        )
        self.btn_excluir_massa.pack(side=tk.LEFT, padx=5)
        
        # Botão para selecionar todos
        self.btn_selecionar_todos = ttk.Button(
            self.frame_botoes,
            text="✓ Selecionar Todos",
            command=self.selecionar_todos,
            style="Info.TButton"
        )
        self.btn_selecionar_todos.pack(side=tk.LEFT, padx=5)
        
        # Label com total de itens (direita)
        self.label_contagem = ttk.Label(
            self.frame_superior,
            text="",
            style="Info.TLabel"
        )
        self.label_contagem.pack(side=tk.RIGHT, padx=5)
        
        # TreeView para listar os códigos
        self.tree = ttk.Treeview(
            self.window,
            columns=(
                "serial",
                "data_leitura",
                "hora_leitura",
                "status",
                "numero_caixa",
                "data_identificacao",
                "hora_identificacao",
                "observacao"
            ),
            show="headings",
            selectmode="extended"  # Permitir seleção múltipla
        )
        
        # Configurar colunas
        self.tree.heading("serial", text="Serial")
        self.tree.heading("data_leitura", text="Data Leitura")
        self.tree.heading("hora_leitura", text="Hora Leitura")
        self.tree.heading("status", text="Status")
        self.tree.heading("numero_caixa", text="Caixa")
        self.tree.heading("data_identificacao", text="Data Identificação")
        self.tree.heading("hora_identificacao", text="Hora Identificação")
        self.tree.heading("observacao", text="Observação")
        
        # Configurar larguras das colunas
        self.tree.column("serial", width=150)
        self.tree.column("data_leitura", width=100)
        self.tree.column("hora_leitura", width=100)
        self.tree.column("status", width=100)
        self.tree.column("numero_caixa", width=100)
        self.tree.column("data_identificacao", width=120)
        self.tree.column("hora_identificacao", width=120)
        self.tree.column("observacao", width=200)
        
        # Configurar cores para as tags
        self.tree.tag_configure("pendente", foreground="orange")
        self.tree.tag_configure("identificado", foreground="green")
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar TreeView e scrollbar
        self.tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Criar menu de contexto
        self.menu_contexto = tk.Menu(self.window, tearoff=0)
        self.menu_contexto.add_command(
            label="🗑️ Excluir Código",
            command=self.excluir_codigo
        )
        self.menu_contexto.add_command(
            label="📦 Atribuir à Caixa",
            command=self.atribuir_caixa
        )
        
        # Adicionar binding para o botão direito do mouse e teclas
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)
        self.window.bind("<Control-a>", self.selecionar_todos)  # Ctrl+A para selecionar todos
        self.window.bind("<Delete>", lambda e: self.excluir_codigo())  # Delete para excluir
        
        # Carregar dados iniciais
        self.atualizar_lista()
        
        # Configurar protocolo de fechamento
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
    
    def atualizar_lista(self):
        """Atualiza a lista de códigos não identificados"""
        # Limpar TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar códigos pendentes
        codigos = self.controller.carregar_codigos()
        
        # Atualizar contador
        total_codigos = len(codigos)
        self.label_contagem.config(
            text=f"Total de códigos não identificados: {total_codigos}"
        )
        
        # Adicionar à TreeView
        for codigo in codigos:
            # Formatar datas
            data_leitura = datetime.strptime(codigo[1], '%Y-%m-%d').strftime('%d/%m/%Y')
            data_identificacao = (
                datetime.strptime(codigo[5], '%Y-%m-%d').strftime('%d/%m/%Y')
                if codigo[5] else "-"
            )
            
            # Definir tag baseada no status
            tag = "identificado" if codigo[3] == "IDENTIFICADO" else "pendente"
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    codigo[0],  # serial
                    data_leitura,
                    codigo[2],  # hora_leitura
                    codigo[3],  # status
                    codigo[4] or "-",  # numero_caixa
                    data_identificacao,
                    codigo[6] or "-",  # hora_identificacao
                    codigo[7] or "-"   # observacao
                ),
                tags=(tag,)
            )
    
    def selecionar_todos(self, event=None):
        """Seleciona todos os itens da tabela"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def excluir_em_massa(self):
        """Exclui todos os itens selecionados"""
        itens_selecionados = self.tree.selection()
        if not itens_selecionados:
            messagebox.showwarning(
                "Atenção",
                "Por favor, selecione pelo menos um código para excluir."
            )
            return
        
        total_itens = len(itens_selecionados)
        if messagebox.askyesno(
            "Confirmar Exclusão em Massa",
            f"Tem certeza que deseja excluir {total_itens} código{'s' if total_itens > 1 else ''}?\n"
            "Esta ação não pode ser desfeita."
        ):
            seriais_excluidos = []
            seriais_com_erro = []
            
            for item in itens_selecionados:
                valores = self.tree.item(item)['values']
                serial = valores[0]  # índice 0 é o serial
                
                sucesso, mensagem = self.controller.excluir_codigo(serial)
                if sucesso:
                    seriais_excluidos.append(serial)
                else:
                    seriais_com_erro.append(f"{serial} ({mensagem})")
            
            # Montar mensagem de resultado
            mensagem = f"✅ {len(seriais_excluidos)} código{'s' if len(seriais_excluidos) > 1 else ''} excluído{'s' if len(seriais_excluidos) > 1 else ''} com sucesso!"
            
            if seriais_com_erro:
                mensagem += "\n\n❌ Erros ao excluir:"
                for erro in seriais_com_erro:
                    mensagem += f"\n• {erro}"
            
            messagebox.showinfo("Resultado da Exclusão", mensagem)
            self.atualizar_lista()
    
    def mostrar_menu_contexto(self, event):
        """Mostra o menu de contexto na posição do clique"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu_contexto.tk_popup(event.x_root, event.y_root)
    
    def ao_fechar(self):
        """Ação ao fechar a janela"""
        self.window.withdraw()  # Apenas esconde a janela ao invés de destruí-la

    def atribuir_caixa(self):
        """Atribui uma caixa ao código selecionado"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning(
                "Atenção",
                "Por favor, selecione um código para atribuir à caixa."
            )
            return
        
        # Obter serial do item selecionado
        item = self.tree.item(selecao[0])
        serial = item['values'][0]
        
        # Confirmar atribuição
        if messagebox.askyesno(
            "Confirmar Atribuição",
            f"Deseja atribuir o código {serial} à caixa atual?"
        ):
            # Atribuir caixa
            sucesso, mensagem = self.controller.atribuir_caixa(serial)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", mensagem)
    
    def excluir_codigo(self):
        """Exclui o código selecionado"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning(
                "Atenção",
                "Por favor, selecione um código para excluir."
            )
            return
        
        # Obter serial do item selecionado
        item = self.tree.item(selecao[0])
        serial = item['values'][0]
        
        # Confirmar exclusão
        if messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o código {serial}?"
        ):
            # Excluir código
            sucesso, mensagem = self.controller.excluir_codigo(serial)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", mensagem) 