import sqlite3
from datetime import datetime
from .database import Database

class Leitura:
    @staticmethod
    def inserir_leitura(serial, pedido, linha_lida):
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        data_leitura = datetime.now().strftime('%Y-%m-%d')
        hora_leitura = datetime.now().strftime('%H:%M:%S')
        
        cursor.execute('''
            INSERT INTO leituras (serial, pedido_lido, linha_lida, data_leitura, hora_leitura)
            VALUES (?, ?, ?, ?, ?)
        ''', (serial, pedido, linha_lida, data_leitura, hora_leitura))
        
        conn.commit()
        conn.close()

    @staticmethod
    def verificar_se_ja_lido(serial):
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM leituras WHERE serial = ?', (serial,))
        resultado = cursor.fetchone()[0] > 0
        
        conn.close()
        return resultado

    @staticmethod
    def buscar_leituras(serial=None):
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        if serial:
            cursor.execute('''
                SELECT l.*, p.nome_status 
                FROM leituras l
                LEFT JOIN produtos p ON l.serial = p.serial
                WHERE l.serial = ?
            ''', (serial,))
        else:
            cursor.execute('''
                SELECT l.*, p.nome_status 
                FROM leituras l
                LEFT JOIN produtos p ON l.serial = p.serial
                ORDER BY l.data_leitura DESC, l.hora_leitura DESC
            ''')
            
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    @staticmethod
    def remover_leitura(serial, data_leitura, hora_leitura):
        """Remove uma leitura específica do banco de dados"""
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM leituras 
                WHERE serial = ? AND data_leitura = ? AND hora_leitura = ?
            ''', (serial, data_leitura, hora_leitura))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao remover leitura: {e}")
            return False
        finally:
            conn.close()