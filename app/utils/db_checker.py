import sqlite3
from app.models.database import Database

def verificar_duplicatas():
    conn = sqlite3.connect(Database.DB_NAME)
    cursor = conn.cursor()
    
    # Verificar duplicatas na tabela produtos
    cursor.execute('''
        SELECT serial, maquina, COUNT(*) as contagem
        FROM produtos
        GROUP BY serial, maquina
        HAVING COUNT(*) > 1
    ''')
    duplicatas_produtos = cursor.fetchall()
    
    # Verificar duplicatas na tabela leituras
    cursor.execute('''
        SELECT serial, pedido_lido, linha_lida, data_leitura, hora_leitura, COUNT(*) as contagem
        FROM leituras
        GROUP BY serial, pedido_lido, linha_lida, data_leitura, hora_leitura
        HAVING COUNT(*) > 1
    ''')
    duplicatas_leituras = cursor.fetchall()
    
    conn.close()
    
    return {
        'produtos': duplicatas_produtos,
        'leituras': duplicatas_leituras
    }

def limpar_duplicatas():
    conn = sqlite3.connect(Database.DB_NAME)
    cursor = conn.cursor()
    
    # Remover duplicatas da tabela produtos mantendo apenas o registro mais recente
    cursor.execute('''
        DELETE FROM produtos
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM produtos
            GROUP BY serial, maquina
        )
    ''')
    
    # Remover duplicatas da tabela leituras mantendo apenas o registro mais recente
    cursor.execute('''
        DELETE FROM leituras
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM leituras
            GROUP BY serial, pedido_lido, linha_lida, data_leitura, hora_leitura
        )
    ''')
    
    conn.commit()
    conn.close()

def adicionar_restricoes():
    conn = sqlite3.connect(Database.DB_NAME)
    cursor = conn.cursor()
    
    # Adicionar índice único para evitar duplicatas na tabela leituras
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_leituras_unico 
        ON leituras(serial, pedido_lido, linha_lida, data_leitura, hora_leitura)
    ''')
    
    conn.commit()
    conn.close() 