from ..models.codigo_nao_identificado import CodigoNaoIdentificado
from ..models.caixa import Caixa
from tkinter import messagebox
import sqlite3
from ..models.database import Database

class CodigosNaoIdentificadosController:
    def __init__(self):
        self.view = None
        self.main_controller = None

    def set_view(self, view):
        self.view = view

    def set_main_controller(self, controller):
        self.main_controller = controller

    def carregar_codigos(self):
        """Carrega todos os códigos não identificados"""
        return CodigoNaoIdentificado.buscar_codigos_pendentes()

    def atribuir_caixa(self, serial):
        """Atribui uma caixa ao código selecionado"""
        # Verificar se há uma caixa aberta
        caixa_atual = Caixa.get_caixa_atual()
        if not caixa_atual:
            return False, "Não há caixa aberta. Por favor, abra uma caixa primeiro."

        # Atribuir caixa
        sucesso, mensagem = CodigoNaoIdentificado.atribuir_caixa(serial, caixa_atual)
        
        # Se atribuiu com sucesso, atualizar a view principal
        if sucesso and self.main_controller:
            # Atualizar a interface principal com o número da caixa atual
            self.main_controller.atualizar_status_caixa()
            self.main_controller.carregar_dados_iniciais()

        return sucesso, mensagem

    def mostrar_view(self):
        """Mostra a view de códigos não identificados"""
        if self.view:
            self.view.atualizar_lista()
            self.view.window.deiconify()  # Mostrar janela se estiver oculta
            self.view.window.focus_force()  # Trazer para frente 

    def excluir_codigo(self, serial):
        """Exclui um código não identificado e seus registros relacionados"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Verificar se o código existe
            cursor.execute('''
                SELECT status FROM codigos_nao_identificados 
                WHERE serial = ?
            ''', (serial,))
            
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Código não encontrado."
            
            # Remover da tabela leituras
            cursor.execute('DELETE FROM leituras WHERE serial = ?', (serial,))
            leituras_removidas = cursor.rowcount
            
            # Remover da tabela codigos_nao_identificados
            cursor.execute('DELETE FROM codigos_nao_identificados WHERE serial = ?', (serial,))
            nao_identificados_removidos = cursor.rowcount
            
            # Remover quaisquer referências em outras tabelas relacionadas
            # Tabela de caixas (se houver referência)
            cursor.execute('''
                UPDATE caixas 
                SET total_itens = total_itens - 1 
                WHERE numero_caixa IN (
                    SELECT DISTINCT numero_caixa 
                    FROM leituras 
                    WHERE serial = ? AND numero_caixa IS NOT NULL
                )
            ''', (serial,))
            
            conn.commit()
            
            # Log detalhado das remoções
            print(f"📊 Estatísticas de remoção para o serial {serial}:")
            print(f"✓ Registros removidos de leituras: {leituras_removidas}")
            print(f"✓ Registros removidos de codigos_nao_identificados: {nao_identificados_removidos}")
            
            # Atualizar todas as interfaces
            if self.main_controller:
                self.main_controller.carregar_dados_iniciais()
                if (hasattr(self.main_controller, 'itens_sem_caixa_controller') and 
                    self.main_controller.itens_sem_caixa_controller is not None):
                    self.main_controller.itens_sem_caixa_controller.atualizar_dados()
            
            return True, f"Código {serial} excluído com sucesso!"
            
        except Exception as e:
            conn.rollback()
            return False, f"Erro ao excluir código: {str(e)}"
        finally:
            conn.close() 