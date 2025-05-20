import os
import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread

PASTA_EXCEL = "excel_importados"
CADASTRO_PRODUTOS = "cadastro_produtos.xlsx"
DB = "dados.db"

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
            data_producao TEXT,
            arquivo TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro_produtos (
            sa_sc TEXT PRIMARY KEY,
            pn TEXT,
            familia TEXT,
            ot TEXT,
            cabo TEXT,
            solda_mae TEXT
        )
    ''')

    conn.commit()
    conn.close()

def importar_cadastro_produtos():
    if not os.path.exists(CADASTRO_PRODUTOS):
        print("Arquivo de cadastro de produtos não encontrado.")
        return

    df = pd.read_excel(CADASTRO_PRODUTOS)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        sa_sc = str(row.get('SA / SC', '')).strip()
        if not sa_sc:
            continue

        cursor.execute('''
            INSERT OR REPLACE INTO cadastro_produtos (sa_sc, pn, familia, ot, cabo, solda_mae)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            sa_sc,
            str(row.get('PN', '')).strip(),
            str(row.get('FAMILIA', '')).strip(),
            str(row.get('OT', '')).strip(),
            str(row.get('CABO', '')).strip(),
            str(row.get('SOLDA MAE', '')).strip()
        ))

    conn.commit()
    conn.close()
    print("Cadastro de produtos atualizado.")

def importar_excel_incremental(caminho):
    try:
        df = pd.read_excel(caminho)
        nome_arquivo = os.path.basename(caminho)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            serial = str(row.get('Serial', '')).strip()
            if not serial:
                continue  # ignora linhas sem código de barras

            cursor.execute('SELECT 1 FROM produtos WHERE serial = ?', (serial,))
            if cursor.fetchone():
                continue  # já existe, pula

            cursor.execute('''
                INSERT INTO produtos (
                    pedido, data_pedido, linha_mae, area, maquina,
                    linha_ato, item, serial, quantidade, nome_status,
                    data_producao, arquivo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                str(row.get('Data Produção', '')).strip(),
                nome_arquivo
            ))

        conn.commit()
        conn.close()
        print(f"Importado: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao importar {caminho}: {e}")

class ExcelHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith((".xlsx", ".xls")):
            importar_excel_incremental(event.src_path)

def iniciar_monitoramento():
    observer = Observer()
    handler = ExcelHandler()
    observer.schedule(handler, path=PASTA_EXCEL, recursive=False)
    observer.start()

def iniciar_interface():
    def verificar_codigo(event=None):
        codigo = entry.get().strip()
        entry.delete(0, tk.END)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                p.item,
                p.quantidade,
                p.arquivo,
                c.familia, c.pn, c.ot, c.cabo, c.solda_mae
            FROM produtos p
            LEFT JOIN cadastro_produtos c ON p.item = c.sa_sc
            WHERE p.serial = ?
        ''', (codigo,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            item, qtd, arquivo, familia, pn, ot, cabo, solda_mae = resultado
            result_label.config(
                text=f"Serial: {codigo} → Item: {item} | Qtde: {qtd} | Arquivo: {arquivo}\n"
                     f"PN: {pn or '-'} | Família: {familia or '-'} | OT: {ot or '-'} | CABO: {cabo or '-'} | SOLDA MAE: {solda_mae or '-'}",
                fg="green"
            )
        else:
            result_label.config(text="Código de barras não encontrado!", fg="orange")

    root = tk.Tk()
    root.title("Leitor de Código de Barras")

    tk.Label(root, text="Escaneie ou digite o código de barras (Serial):").pack()
    entry = tk.Entry(root, width=40)
    entry.pack(pady=10)
    entry.focus()
    entry.bind("<Return>", verificar_codigo)

    result_label = tk.Label(root, text="", font=("Arial", 12))
    result_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    os.makedirs(PASTA_EXCEL, exist_ok=True)
    criar_banco()
    importar_cadastro_produtos()
    Thread(target=iniciar_monitoramento, daemon=True).start()
    iniciar_interface()
