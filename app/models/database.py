import sqlite3
import os

class Database:
    DB_NAME = 'dados.db'

    @staticmethod
    def criar_banco():
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido TEXT,
                data_pedido DATE,
                linha_mae TEXT,
                area TEXT,
                maquina TEXT,
                linha_ato TEXT,
                item TEXT,
                serial TEXT,
                quantidade INTEGER,
                nome_status TEXT,
                data_producao DATE,
                UNIQUE(serial, maquina)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leituras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial TEXT,
                pedido_lido TEXT,
                linha_lida TEXT,
                data_leitura DATE,
                hora_leitura TIME,
                numero_caixa TEXT,
                status_caixa TEXT DEFAULT 'ABERTA'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS caixas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_caixa TEXT UNIQUE,
                data_abertura DATE,
                hora_abertura TIME,
                data_fechamento DATE,
                hora_fechamento TIME,
                status TEXT DEFAULT 'ABERTA',
                total_itens INTEGER DEFAULT 0,
                usuario_fechamento TEXT,
                reaberturas INTEGER DEFAULT 0
            )
        ''')

        # Adicionar coluna usuario_fechamento se não existir
        try:
            cursor.execute('ALTER TABLE caixas ADD COLUMN usuario_fechamento TEXT')
        except sqlite3.OperationalError:
            # Coluna já existe, ignorar erro
            pass

        # Adicionar coluna reaberturas se não existir
        try:
            cursor.execute('ALTER TABLE caixas ADD COLUMN reaberturas INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            # Coluna já existe, ignorar erro
            pass

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS codigos_nao_identificados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial TEXT UNIQUE,
                data_leitura DATE,
                hora_leitura TIME,
                status TEXT DEFAULT 'PENDENTE',
                numero_caixa TEXT,
                data_identificacao DATE,
                hora_identificacao TIME,
                observacao TEXT
            )
        ''')

        conn.commit()
        conn.close()