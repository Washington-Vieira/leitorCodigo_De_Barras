import sqlite3

DB = "dados.db"

def listar_tabelas():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Listar todas as tabelas no banco de dados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    print("Tabelas no banco de dados:")
    for tabela in tabelas:
        print(f"- {tabela[0]}")

    conn.close()

def ler_tabela(nome_tabela):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Ler os dados da tabela especificada
    try:
        cursor.execute(f"SELECT * FROM {nome_tabela}")
        colunas = [description[0] for description in cursor.description]
        print(f"\nDados da tabela '{nome_tabela}':")
        print(f"Colunas: {colunas}")
        for linha in cursor.fetchall():
            print(linha)
    except sqlite3.Error as e:
        print(f"Erro ao acessar a tabela '{nome_tabela}': {e}")

    conn.close()

if __name__ == "__main__":
    listar_tabelas()
    tabela = input("\nDigite o nome da tabela para visualizar os dados: ").strip()
    ler_tabela(tabela)