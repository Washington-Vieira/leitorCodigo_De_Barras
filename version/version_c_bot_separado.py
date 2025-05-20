import os
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import unicodedata

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

def normalizar_coluna(col):
    col = col.strip().replace('\xa0', ' ')
    col = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode()
    return col

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
            df.columns = [normalizar_coluna(col) for col in df.columns]

            for _, row in df.iterrows():
                serial = str(row.get('Serial', '')).strip()
                maquina = str(row.get('Maquina', '')).strip()
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
                            str(row.get('Area', '')).strip(),
                            str(row.get('Linha ATO', '')).strip(),
                            str(row.get('Item', '')).strip(),
                            int(row.get('Quantidade', 0)),
                            nome_status_novo,
                            str(row.get('Data Producao', '')).strip(),
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
                            str(row.get('Area', '')).strip(),
                            maquina,
                            str(row.get('Linha ATO', '')).strip(),
                            str(row.get('Item', '')).strip(),
                            serial,
                            int(row.get('Quantidade', 0)),
                            str(row.get('Nome Status', '')).strip(),
                            str(row.get('Data Producao', '')).strip()
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

def abrir_resumo_status(status):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    resumo_win = tk.Toplevel()
    resumo_win.title(f"Resumo - Status: {status}")
    resumo_win.geometry("1000x400")

    search_var = tk.StringVar()

    frame_top = tk.Frame(resumo_win)
    frame_top.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_top, text="Pesquisar:").pack(side="left")
    search_entry = tk.Entry(frame_top, textvariable=search_var)
    search_entry.pack(side="left", padx=5)

    tree = ttk.Treeview(resumo_win, columns=("Pedido", "Máquina", "Item", "Status", "Total Quantidade"), show="headings")
    for col in ("Pedido", "Máquina", "Item", "Status", "Total Quantidade"):
        tree.heading(col, text=col)
        tree.column(col, width=180)
    tree.pack(fill="both", expand=True)

    def carregar_dados():
        tree.delete(*tree.get_children())
        cursor.execute('''
            SELECT pedido, maquina, item, nome_status, SUM(quantidade)
            FROM produtos
            WHERE nome_status = ?
            GROUP BY pedido, maquina, item, nome_status
        ''', (status,))
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def filtrar(*args):
        termo = search_var.get().lower()
        tree.delete(*tree.get_children())
        cursor.execute('''
            SELECT pedido, maquina, item, nome_status, SUM(quantidade)
            FROM produtos
            WHERE nome_status = ?
            GROUP BY pedido, maquina, item, nome_status
        ''', (status,))
        for row in cursor.fetchall():
            if any(termo in str(valor).lower() for valor in row):
                tree.insert("", tk.END, values=row)

    search_var.trace_add("write", filtrar)
    carregar_dados()

    resumo_win.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), resumo_win.destroy()))

def leitor_codigo_barras_gui():
    def verificar_codigo(event=None):
        codigo = entry_codigo.get().strip().lstrip("0")
        entry_codigo.delete(0, tk.END)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM produtos WHERE serial = ?", (codigo,))
        resultado = cursor.fetchone()

        if resultado:
            serial = resultado[8]
            cursor.execute("SELECT 1 FROM leituras WHERE serial = ?", (serial,))
            ja_lido = cursor.fetchone()

            if not ja_lido:
                pedido = resultado[1]
                linha_ato = resultado[6]
                item = resultado[7]
                maquina = resultado[5]
                quantidade = resultado[9]
                status = resultado[10]
                linha_lida = linha_ato[:4] if linha_ato else ''
                data_leitura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute('''
                    INSERT INTO leituras (serial, pedido_lido, linha_lida, data_leitura)
                    VALUES (?, ?, ?, ?)
                ''', (serial, pedido, linha_lida, data_leitura))

                tree.insert("", tk.END, values=(pedido, serial, item, maquina, linha_lida, quantidade, status, data_leitura))
            else:
                print(f"⚠️ Código '{codigo}' já foi lido anteriormente.")
        else:
            print(f"❌ Código '{codigo}' não encontrado no banco de dados.")
            tree.insert("", tk.END, values=(codigo, "❌ Não encontrado", "-", "-", "-", "-", "-", "-"))

        conn.commit()
        conn.close()

    root = tk.Tk()
    root.title("Leitor de Código de Barras")
    root.geometry("1000x500")

    top_frame = tk.Frame(root)
    top_frame.pack(pady=5)

    label = tk.Label(top_frame, text="Escaneie o código de barras:")
    label.pack(side="left")

    entry_codigo = tk.Entry(top_frame, font=("Arial", 14), width=40)
    entry_codigo.pack(side="left", padx=10)
    entry_codigo.focus()
    entry_codigo.bind("<Return>", verificar_codigo)

    botao_pendente = tk.Button(top_frame, text="📋 Pendentes", command=lambda: abrir_resumo_status("PENDENTE"))
    botao_pendente.pack(side="left", padx=5)

    botao_andamento = tk.Button(top_frame, text="🔄 Em Andamento", command=lambda: abrir_resumo_status("EM ANDAMENTO"))
    botao_andamento.pack(side="left", padx=5)

    botao_concluido = tk.Button(top_frame, text="✅ Concluídos", command=lambda: abrir_resumo_status("CONCLUÍDO"))
    botao_concluido.pack(side="left", padx=5)

    colunas = ("Pedido", "Serial", "Item", "Máquina", "Linha", "Quantidade", "Status", "Data/Hora Leitura")
    tree = ttk.Treeview(root, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(pady=10, fill="both", expand=True)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.pedido_lido, l.serial, p.item, p.maquina, l.linha_lida, p.quantidade, p.nome_status, l.data_leitura
        FROM leituras l
        LEFT JOIN produtos p ON l.serial = p.serial
        ORDER BY l.data_leitura ASC
    ''')
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

    root.mainloop()

if __name__ == "__main__":
    criar_banco()
    importar_excels_para_sqlite()
    leitor_codigo_barras_gui()