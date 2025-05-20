import os
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

PASTA_EXCEL = 'excel_importados'
DB = 'dados.db'

def criar_banco():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido TEXT,
            data_pedido TEXT,
            linha_mae TEXT,
            area TEXT,
            maquina TEXT,
            linha_ato TEXT,
            item TEXT,
            serial TEXT,
            quantidade INTEGER,
            nome_status TEXT,
            data_producao TEXT,
            UNIQUE(serial, maquina)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial TEXT,
            pedido_lido TEXT,
            linha_lida TEXT,
            data_leitura TEXT
        )
    ''')

    conn.commit()
    conn.close()

def importar_excels_para_sqlite():
    if not os.path.exists(PASTA_EXCEL):
        os.makedirs(PASTA_EXCEL)
        print(f"⚠️ Pasta '{PASTA_EXCEL}' criada. Coloque os arquivos Excel lá e execute novamente.")
        return

    arquivos = [f for f in os.listdir(PASTA_EXCEL) if f.endswith(('.xlsx', '.xls'))]
    if not arquivos:
        print(f"⚠️ Nenhum arquivo Excel encontrado na pasta '{PASTA_EXCEL}'.")
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    total_inseridos = 0
    total_atualizados = 0
    total_ignorados = 0

    for arquivo in arquivos:
        caminho = os.path.join(PASTA_EXCEL, arquivo)

        inseridos = 0
        ignorados = 0
        atualizados = 0

        try:
            df = pd.read_excel(caminho)

            for _, row in df.iterrows():
                serial = str(row.get('Serial', '')).strip()
                maquina = str(row.get('Máquina', '')).strip()
                if not serial:
                    continue

                cursor.execute("SELECT nome_status FROM produtos WHERE serial = ? AND maquina = ?", (serial, maquina))
                resultado = cursor.fetchone()

                if resultado:
                    nome_status_existente = resultado[0]
                    nome_status_novo = str(row.get('Nome Status', '')).strip()

                    if nome_status_existente != nome_status_novo:
                        cursor.execute('''
                            UPDATE produtos SET
                                pedido = ?, data_pedido = ?, linha_mae = ?, area = ?, 
                                linha_ato = ?, item = ?, quantidade = ?, 
                                nome_status = ?, data_producao = ?
                            WHERE serial = ? AND maquina = ?
                        ''', (
                            str(row.get('Pedido', '')).strip(),
                            str(row.get('Data Pedido', '')).strip(),
                            str(row.get('Linha MAE', '')).strip(),
                            str(row.get('Área', '')).strip(),
                            str(row.get('Linha ATO', '')).strip(),
                            str(row.get('Item', '')).strip(),
                            int(row.get('Quantidade', 0)),
                            nome_status_novo,
                            str(row.get('Data Produção', '')).strip(),
                            serial,
                            maquina
                        ))
                        atualizados += 1
                    else:
                        ignorados += 1
                else:
                    try:
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
                            maquina,
                            str(row.get('Linha ATO', '')).strip(),
                            str(row.get('Item', '')).strip(),
                            serial,
                            int(row.get('Quantidade', 0)),
                            str(row.get('Nome Status', '')).strip(),
                            str(row.get('Data Produção', '')).strip()
                        ))
                        inseridos += 1
                    except sqlite3.IntegrityError:
                        ignorados += 1

            total_inseridos += inseridos
            total_atualizados += atualizados
            total_ignorados += ignorados

            print(f"\n📁 {arquivo} importado:")
            print(f"   ➕ Inseridos   : {inseridos}")
            print(f"   🔁 Atualizados: {atualizados}")
            print(f"   ❌ Ignorados  : {ignorados}")

        except Exception as e:
            print(f"❌ Erro ao importar {arquivo}: {e}")

    conn.commit()
    conn.close()

    print("\n📊 RESUMO TOTAL:")
    print(f"   ➕ Total inseridos   : {total_inseridos}")
    print(f"   🔁 Total atualizados: {total_atualizados}")
    print(f"   ❌ Total ignorados  : {total_ignorados}")

def leitor_codigo_barras_gui():
    def verificar_codigo(event=None):
        codigo = entry_codigo.get().strip().lstrip("0")
        entry_codigo.delete(0, tk.END)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        # Verificar se o código já foi lido
        cursor.execute("SELECT COUNT(*) FROM leituras WHERE serial = ?", (codigo,))
        if cursor.fetchone()[0] > 0:
            messagebox.showinfo("Aviso", f"⚠️ Código '{codigo}' já foi lido anteriormente.")
            conn.close()
            return

        cursor.execute("""
            SELECT pedido, linha_ato, item, maquina, quantidade, nome_status 
            FROM produtos WHERE serial = ?
        """, (codigo,))
        resultado = cursor.fetchone()

        if resultado:
            pedido = resultado[0]
            linha_ato = resultado[1]
            item = resultado[2]
            maquina = resultado[3]
            quantidade = resultado[4]
            status = resultado[5]

            linha_lida = linha_ato[:4] if linha_ato else ''
            data_leitura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                INSERT INTO leituras (serial, pedido_lido, linha_lida, data_leitura)
                VALUES (?, ?, ?, ?)
            ''', (codigo, pedido, linha_lida, data_leitura))

            conn.commit()

            tree.insert("", tk.END, values=(pedido, codigo, item, maquina, linha_lida, quantidade, status, data_leitura))
        else:
            tree.insert("", tk.END, values=(codigo, "❌ Não encontrado", "-", "-", "-", "-", "-", "-"))

        conn.close()

    root = tk.Tk()
    root.title("Leitor de Código de Barras")
    root.geometry("950x350")

    label = tk.Label(root, text="Escaneie o código de barras:")
    label.pack(pady=5)

    entry_codigo = tk.Entry(root, font=("Arial", 14), width=40)
    entry_codigo.pack(pady=5)
    entry_codigo.focus()
    entry_codigo.bind("<Return>", verificar_codigo)

    colunas = ("Pedido", "Serial", "Item", "Máquina", "Linha", "Quantidade", "Status", "Data/Hora Leitura")
    tree = ttk.Treeview(root, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(pady=10, fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    criar_banco()
    importar_excels_para_sqlite()
    leitor_codigo_barras_gui()