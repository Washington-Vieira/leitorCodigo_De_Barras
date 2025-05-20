import sqlite3
from datetime import datetime
from .database import Database

class Caixa:
    @staticmethod
    def abrir_caixa(numero_caixa):
        """Abre uma nova caixa"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Verificar se já existe uma caixa aberta
            cursor.execute('SELECT numero_caixa FROM caixas WHERE status = "ABERTA"')
            caixa_aberta = cursor.fetchone()
            if caixa_aberta:
                conn.close()
                return False, f"Já existe uma caixa aberta: {caixa_aberta[0]}"
            
            # Verificar se o número da caixa já foi usado
            cursor.execute('SELECT status FROM caixas WHERE numero_caixa = ?', (numero_caixa,))
            caixa_existente = cursor.fetchone()
            if caixa_existente:
                conn.close()
                return False, f"Número de caixa já utilizado: {numero_caixa}"
            
            # Inserir nova caixa
            data_atual = datetime.now().strftime('%Y-%m-%d')
            hora_atual = datetime.now().strftime('%H:%M:%S')
            
            cursor.execute('''
                INSERT INTO caixas (
                    numero_caixa, data_abertura, hora_abertura, status
                ) VALUES (?, ?, ?, "ABERTA")
            ''', (numero_caixa, data_atual, hora_atual))
            
            conn.commit()
            conn.close()
            return True, "Caixa aberta com sucesso!"
            
        except Exception as e:
            conn.close()
            return False, f"Erro ao abrir caixa: {str(e)}"
    
    @staticmethod
    def fechar_caixa():
        """Fecha a caixa atualmente aberta"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Buscar caixa aberta
            cursor.execute('SELECT numero_caixa FROM caixas WHERE status = "ABERTA"')
            caixa_aberta = cursor.fetchone()
            
            if not caixa_aberta:
                conn.close()
                return False, "Não há caixa aberta para fechar"
            
            numero_caixa = caixa_aberta[0]
            data_atual = datetime.now().strftime('%Y-%m-%d')
            hora_atual = datetime.now().strftime('%H:%M:%S')
            
            # Contar total de itens na caixa
            cursor.execute('''
                SELECT COUNT(*) FROM leituras 
                WHERE numero_caixa = ? AND status_caixa = "ABERTA"
            ''', (numero_caixa,))
            total_itens = cursor.fetchone()[0]
            
            # Atualizar status da caixa
            cursor.execute('''
                UPDATE caixas 
                SET status = "FECHADA",
                    data_fechamento = ?,
                    hora_fechamento = ?,
                    total_itens = ?,
                    usuario_fechamento = "Sistema"
                WHERE numero_caixa = ?
            ''', (data_atual, hora_atual, total_itens, numero_caixa))
            
            # Atualizar status das leituras desta caixa
            cursor.execute('''
                UPDATE leituras 
                SET status_caixa = "FECHADA"
                WHERE numero_caixa = ? AND status_caixa = "ABERTA"
            ''', (numero_caixa,))
            
            conn.commit()
            conn.close()
            return True, f"Caixa {numero_caixa} fechada com sucesso! Total de itens: {total_itens}"
            
        except Exception as e:
            conn.close()
            return False, f"Erro ao fechar caixa: {str(e)}"
    
    @staticmethod
    def get_caixa_atual():
        """Retorna o número da caixa atualmente aberta"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT numero_caixa FROM caixas WHERE status = "ABERTA"')
        resultado = cursor.fetchone()
        
        conn.close()
        return resultado[0] if resultado else None
    
    @staticmethod
    def atualizar_leitura_com_caixa(serial, numero_caixa):
        """Atualiza uma leitura com o número da caixa"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE leituras 
                SET numero_caixa = ?, status_caixa = "ABERTA"
                WHERE serial = ? AND numero_caixa IS NULL
            ''', (numero_caixa, serial))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            return False
    
    @staticmethod
    def excluir_caixa(numero_caixa):
        """Exclui uma caixa e todas as suas leituras"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Verificar se a caixa existe
            cursor.execute('SELECT status FROM caixas WHERE numero_caixa = ?', (numero_caixa,))
            caixa = cursor.fetchone()
            
            if not caixa:
                conn.close()
                return False, "Caixa não encontrada."
            
            # Iniciar transação
            cursor.execute('BEGIN TRANSACTION')
            
            # Remover referência da caixa nas leituras
            cursor.execute('''
                UPDATE leituras 
                SET numero_caixa = NULL, status_caixa = NULL
                WHERE numero_caixa = ?
            ''', (numero_caixa,))
            
            # Excluir a caixa
            cursor.execute('DELETE FROM caixas WHERE numero_caixa = ?', (numero_caixa,))
            
            cursor.execute('COMMIT')
            conn.close()
            return True, f"Caixa {numero_caixa} excluída com sucesso!"
            
        except Exception as e:
            cursor.execute('ROLLBACK')
            conn.close()
            return False, f"Erro ao excluir caixa: {str(e)}"
    
    @staticmethod
    def excluir_item_caixa(numero_caixa, serial):
        """Remove um item específico de uma caixa"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Verificar se o item está na caixa
            cursor.execute('''
                SELECT l.id, c.status 
                FROM leituras l
                JOIN caixas c ON l.numero_caixa = c.numero_caixa
                WHERE l.numero_caixa = ? AND l.serial = ?
            ''', (numero_caixa, serial))
            
            resultado = cursor.fetchone()
            if not resultado:
                conn.close()
                return False, "Item não encontrado na caixa especificada."
            
            leitura_id, status_caixa = resultado
            
            # Iniciar transação
            cursor.execute('BEGIN TRANSACTION')
            
            # Remover referência da caixa na leitura
            cursor.execute('''
                UPDATE leituras 
                SET numero_caixa = NULL, status_caixa = NULL
                WHERE id = ?
            ''', (leitura_id,))
            
            # Atualizar total de itens na caixa
            cursor.execute('''
                UPDATE caixas 
                SET total_itens = (
                    SELECT COUNT(*) 
                    FROM leituras 
                    WHERE numero_caixa = ?
                )
                WHERE numero_caixa = ?
            ''', (numero_caixa, numero_caixa))
            
            cursor.execute('COMMIT')
            conn.close()
            return True, f"Item {serial} removido da caixa {numero_caixa} com sucesso!"
            
        except Exception as e:
            cursor.execute('ROLLBACK')
            conn.close()
            return False, f"Erro ao remover item da caixa: {str(e)}"
    
    @staticmethod
    def reabrir_caixa(numero_caixa):
        """Reabre uma caixa fechada se não excedeu o limite de reaberturas"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Verificar se a caixa existe e está fechada
            cursor.execute('''
                SELECT status, reaberturas 
                FROM caixas 
                WHERE numero_caixa = ?
            ''', (numero_caixa,))
            
            resultado = cursor.fetchone()
            if not resultado:
                conn.close()
                return False, "Caixa não encontrada."
            
            status, reaberturas = resultado
            
            if status != "FECHADA":
                conn.close()
                return False, "Esta caixa não está fechada."
            
            if reaberturas >= 2:
                conn.close()
                return False, "Esta caixa já atingiu o limite máximo de 2 reaberturas."
            
            # Atualizar status da caixa
            data_atual = datetime.now().strftime('%Y-%m-%d')
            hora_atual = datetime.now().strftime('%H:%M:%S')
            
            cursor.execute('''
                UPDATE caixas 
                SET status = "ABERTA",
                    data_abertura = ?,
                    hora_abertura = ?,
                    reaberturas = reaberturas + 1
                WHERE numero_caixa = ?
            ''', (data_atual, hora_atual, numero_caixa))
            
            # Atualizar status das leituras desta caixa
            cursor.execute('''
                UPDATE leituras 
                SET status_caixa = "ABERTA"
                WHERE numero_caixa = ?
            ''', (numero_caixa,))
            
            conn.commit()
            conn.close()
            return True, f"Caixa {numero_caixa} reaberta com sucesso!"
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Erro ao reabrir caixa: {str(e)}" 