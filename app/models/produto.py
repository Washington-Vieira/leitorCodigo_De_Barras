from datetime import datetime
from .database import Database
import sqlite3

class Produto:
    @staticmethod
    def buscar_por_serial(serial):
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        # Buscar todos os registros com o mesmo serial
        cursor.execute("SELECT * FROM produtos WHERE serial = ?", (serial,))
        resultados = cursor.fetchall()
        
        if resultados:
            # Se houver mais de um resultado, pegar o primeiro
            resultado = resultados[0]
            
            # Extrair os dados do produto
            pedido = resultado[1]  # pedido
            data_pedido = resultado[2]  # data_pedido
            linha_ato = resultado[6]  # linha_ato
            item = resultado[7]  # item
            maquina = resultado[5]  # maquina
            quantidade = resultado[9]  # quantidade
            status = resultado[10]  # status
            
            # Extrair os primeiros 4 caracteres da linha_ato para linha_lida
            linha_lida = linha_ato[:4] if linha_ato else ''
            
            # Retorna na mesma ordem que a consulta original esperava:
            # (pedido_lido, data_pedido, serial, item, maquina, linha_lida, quantidade, qtd_enviada, status, data_leitura, hora_leitura)
            return (pedido, data_pedido, serial, item, maquina, linha_lida, quantidade, quantidade, status, None, None)
        
        conn.close()
        return None

    @staticmethod
    def inserir_ou_atualizar(dados, serial, maquina):
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO produtos (
                    pedido, data_pedido, linha_mae, area, maquina,
                    linha_ato, item, serial, quantidade, nome_status, data_producao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', dados)
            resultado = "inserido"
        except sqlite3.IntegrityError:
            cursor.execute('''
                UPDATE produtos SET
                    pedido = ?, data_pedido = ?, linha_mae = ?, area = ?, 
                    linha_ato = ?, item = ?, quantidade = ?, 
                    nome_status = ?, data_producao = ?
                WHERE serial = ? AND maquina = ?
            ''', (*dados[:7], dados[9:], serial, maquina))
            resultado = "atualizado"
            
        conn.commit()
        conn.close()
        return resultado