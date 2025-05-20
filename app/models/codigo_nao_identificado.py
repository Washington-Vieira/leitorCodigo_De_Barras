import sqlite3
from datetime import datetime
from .database import Database

class CodigoNaoIdentificado:
    _callback = None
    
    @classmethod
    def set_callback(cls, callback):
        """Define o callback para notificar quando um código for identificado"""
        cls._callback = callback
    
    @staticmethod
    def registrar_codigo(serial):
        """Registra um código não identificado no banco de dados"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Verificar se o código já existe e seu status
            cursor.execute('''
                SELECT status, data_identificacao 
                FROM codigos_nao_identificados 
                WHERE serial = ?
            ''', (serial,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                status_atual = resultado[0]
                data_identificacao = resultado[1]
                
                # Se já está identificado, retornar falso
                if status_atual == 'IDENTIFICADO':
                    return False, "Código já foi identificado anteriormente."
                
                # Se está pendente e é do mesmo dia, retornar falso
                if status_atual == 'PENDENTE' and data_identificacao == datetime.now().strftime('%Y-%m-%d'):
                    return False, "Código já está registrado como não identificado hoje."
                
                # Se está pendente mas é de outro dia, atualizar a data
                cursor.execute('''
                    UPDATE codigos_nao_identificados
                    SET data_leitura = ?,
                        hora_leitura = ?
                    WHERE serial = ?
                ''', (
                    datetime.now().strftime('%Y-%m-%d'),
                    datetime.now().strftime('%H:%M:%S'),
                    serial
                ))
                
                conn.commit()
                return True, "Código atualizado com sucesso!"
            
            # Se não existe, inserir novo registro
            data_atual = datetime.now().strftime('%Y-%m-%d')
            hora_atual = datetime.now().strftime('%H:%M:%S')
            
            cursor.execute('''
                INSERT INTO codigos_nao_identificados (
                    serial, data_leitura, hora_leitura, status
                ) VALUES (?, ?, ?, 'PENDENTE')
            ''', (serial, data_atual, hora_atual))
            
            conn.commit()
            return True, "Código registrado com sucesso!"
            
        except sqlite3.IntegrityError:
            return False, "Código já registrado anteriormente."
        except Exception as e:
            return False, f"Erro ao registrar código: {str(e)}"
        finally:
            conn.close()
    
    @classmethod
    def atualizar_status(cls, serial, identificado=True, numero_caixa=None, observacao=None):
        """Atualiza o status de um código quando ele é identificado"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Verificar se o código já foi processado
            cursor.execute('''
                SELECT status, numero_caixa, data_leitura, hora_leitura
                FROM codigos_nao_identificados
                WHERE serial = ?
            ''', (serial,))
            
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Código não encontrado na tabela de não identificados."
                
            status_atual, caixa_atual, data_leitura_original, hora_leitura_original = resultado
            if status_atual == 'IDENTIFICADO' and identificado:
                return False, "Código já foi identificado anteriormente."
            
            data_atual = datetime.now().strftime('%Y-%m-%d')
            hora_atual = datetime.now().strftime('%H:%M:%S')
            
            if identificado:
                # Buscar informações do produto
                cursor.execute('''
                    SELECT pedido, linha_ato
                    FROM produtos
                    WHERE serial = ?
                ''', (serial,))
                
                produto = cursor.fetchone()
                if produto:
                    pedido, linha_ato = produto
                    linha_lida = linha_ato[:4] if linha_ato else ''
                    
                    # Adicionar diretamente à tabela de leituras sem verificação prévia
                    # para garantir que o registro seja criado
                    try:
                        # Primeiro, verificar se já existe para evitar duplicação
                        cursor.execute('''
                            SELECT id FROM leituras WHERE serial = ?
                        ''', (serial,))
                        
                        leitura_existente = cursor.fetchone()
                        
                        if not leitura_existente:
                            # Inserir na tabela de leituras
                            cursor.execute('''
                                INSERT INTO leituras (
                                    serial, pedido_lido, linha_lida, 
                                    data_leitura, hora_leitura,
                                    status_caixa, numero_caixa
                                ) VALUES (?, ?, ?, ?, ?, 'SEM_CAIXA', NULL)
                            ''', (
                                serial, pedido, linha_lida,
                                data_leitura_original, hora_leitura_original
                            ))
                            print(f"✓ Leitura inserida para o código {serial}")
                        else:
                            print(f"ℹ️ Leitura já existe para o código {serial}")
                    except Exception as e:
                        print(f"⚠️ Erro ao inserir leitura: {str(e)}")
                    
                    # Atualizar a tabela de códigos não identificados
                    cursor.execute('''
                        UPDATE codigos_nao_identificados
                        SET status = 'IDENTIFICADO',
                            numero_caixa = ?,
                            data_identificacao = ?,
                            hora_identificacao = ?,
                            observacao = ?
                        WHERE serial = ?
                    ''', (numero_caixa, data_atual, hora_atual, observacao, serial))
                    
                    conn.commit()
                    
                    # Notificar a interface
                    if cls._callback:
                        # Notificar que o código foi identificado
                        cls._callback(serial, "CODIGO_IDENTIFICADO")
                        # Notificar para atualizar a tela de itens sem caixa
                        cls._callback(serial, "ATUALIZAR_ITENS_SEM_CAIXA")
                        # Notificar para atualizar a tela de códigos não identificados
                        cls._callback(serial, "ATUALIZAR_CODIGOS_NAO_IDENTIFICADOS")
                    
                    return True, "Código identificado e processado com sucesso!"
                else:
                    return False, "Produto não encontrado no banco de dados."
            else:
                # Se não foi identificado, apenas atualizar o status
                cursor.execute('''
                    UPDATE codigos_nao_identificados
                    SET status = ?,
                        numero_caixa = ?,
                        data_identificacao = ?,
                        hora_identificacao = ?,
                        observacao = ?
                    WHERE serial = ?
                ''', ('PENDENTE', numero_caixa, data_atual, hora_atual, observacao, serial))
                
                conn.commit()
                return True, "Status atualizado com sucesso!"
                
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Erro de integridade: {str(e)}")
            return False, f"Erro de integridade: {str(e)}"
        except Exception as e:
            print(f"⚠️ Erro ao atualizar status: {str(e)}")
            return False, f"Erro ao atualizar status: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def buscar_codigos_pendentes():
        """Retorna todos os códigos não identificados pendentes"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    serial, 
                    data_leitura, 
                    hora_leitura, 
                    status,
                    numero_caixa,
                    data_identificacao,
                    hora_identificacao,
                    observacao
                FROM codigos_nao_identificados
                WHERE status = 'PENDENTE'
                ORDER BY data_leitura DESC, hora_leitura DESC
            ''')
            
            return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def atribuir_caixa(serial, numero_caixa):
        """Atribui uma caixa a um código não identificado"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            data_atual = datetime.now().strftime('%Y-%m-%d')
            hora_atual = datetime.now().strftime('%H:%M:%S')
            
            cursor.execute('''
                UPDATE codigos_nao_identificados
                SET numero_caixa = ?,
                    data_identificacao = ?,
                    hora_identificacao = ?
                WHERE serial = ?
            ''', (numero_caixa, data_atual, hora_atual, serial))
            
            conn.commit()
            return True, f"Código {serial} atribuído à caixa {numero_caixa}"
        except Exception as e:
            return False, f"Erro ao atribuir caixa: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def verificar_se_existe(serial):
        """Verifica se um código já está registrado como não identificado"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT status
                FROM codigos_nao_identificados
                WHERE serial = ?
            ''', (serial,))
            
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        finally:
            conn.close() 