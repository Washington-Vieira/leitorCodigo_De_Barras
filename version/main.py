import os
import pandas as pd
import sqlite3
import tkinter as tk

# Constantes
PASTA_EXCEL = "excel_importados"
DB = "dados.db"

# Cria o banco e a tabela se não existir
def criar_banco():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            pedido TEXT,
            data_pedido TEXT,
            linha_mae TEXT,
            area TEXT,
            maquina TEXT,
            linha_ato TEXT,
            item TEXT,
            serial TEXT PRIMARY KEY,
            quantidade INTEGER,
            nome_status TEXT,
            data_producao TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Lê arquivos da pasta e importa para o banco
def importar_excels_para_sqlite():
    arquivos = [f for f in os.listdir(PASTA_EXCEL) if f.endswith(('.xlsx', '.xls'))]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    for arquivo in arquivos:
        caminho = os.path.join(PASTA_EXCEL, arquivo)
        try:
            df = pd.read_excel(caminho)

            for _, row in df.iterrows():
                serial = str(row.get('Serial', '')).strip()
                if not serial:
                    continue

                cursor.execute("SELECT 1 FROM produtos WHERE serial = ?", (serial,))
                if cursor.fetchone():
                    continue  # Já existe, pula

                cursor.execute('''
                    INSERT INTO produtos (
                        pedido, data_pedido, linha_mae, area, maquina,
                        linha_ato, item, serial, quantidade, nome_status, data_producao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row.get('Pedido', '')).strip(),
                    str(row.get('Data Pedido', '')).strip(),
                    str(row.get('Linha MAE', '')).strip(),
                    str(row.get('Área', '')).strip(),
                    str(row.get('Máquina', '')).strip(),
                    str(row.get('Linha ATO', '')).strip(),
                    str(row.get('Item', '')).strip(),
                    serial,
                    int(row.get('Quantidade', 0)),
                    str(row.get('Nome Status', '')).strip(),
                    str(row.get('Data Produção', '')).strip()
                ))
            print(f"✅ Importado com sucesso: {arquivo}")
        except Exception as e:
            print(f"❌ Erro ao importar {arquivo}: {e}")

    conn.commit()
    conn.close()

# Mostra os dados salvos
def mostrar_dados_sqlite():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    print("\n📋 DADOS NO BANCO:")
    print(df.to_string(index=False))

# Interface de leitura de código de barras
def iniciar_leitor_codigos():
    def buscar_serial(event=None):
        codigo = entry.get().strip().replace('\n', '').replace('\r', '')
        if codigo.startswith("0"):
            codigo = codigo[1:]  # Remove o zero inicial, se houver
        entry.delete(0, tk.END)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE serial = ?", (codigo,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            (
                pedido, data_pedido, linha_mae, area, maquina,
                linha_ato, item, serial, quantidade, nome_status, data_producao
            ) = resultado

            msg = (
                f"✅ CÓDIGO ENCONTRADO:\n\n"
                f"Serial: {serial}\n"
                f"Item: {item}\n"
                f"Pedido: {pedido}\n"
                f"Quantidade: {quantidade}\n"
                f"Data Pedido: {data_pedido}\n"
                f"Linha MAE: {linha_mae}\n"
                f"Área: {area}\n"
                f"Máquina: {maquina}\n"
                f"Linha ATO: {linha_ato}\n"
                f"Status: {nome_status}\n"
                f"Data Produção: {data_producao}"
            )
            result_label.config(text=msg, fg="green")
        else:
            result_label.config(text=f"❌ Código '{codigo}' não encontrado no banco!", fg="red")

    # Interface gráfica
    root = tk.Tk()
    root.title("Leitor de Código de Barras")
    root.geometry("700x420")

    tk.Label(root, text="Escaneie ou digite o código de barras:", font=("Arial", 14)).pack(pady=10)
    entry = tk.Entry(root, font=("Arial", 14), width=40)
    entry.pack()
    entry.focus()
    entry.bind("<Return>", buscar_serial)

    result_label = tk.Label(root, text="", font=("Arial", 12), wraplength=660, justify="left")
    result_label.pack(pady=20)

    root.mainloop()

# Execução principal
if __name__ == "__main__":
    os.makedirs(PASTA_EXCEL, exist_ok=True)
    criar_banco()
    importar_excels_para_sqlite()
    mostrar_dados_sqlite()
    iniciar_leitor_codigos()
