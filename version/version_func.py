import os
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import simpledialog

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

    print("\n📋 DADOS ATUAIS NO BANCO:")
    df_final = pd.read_sql_query("SELECT * FROM produtos", conn)
    print(df_final.to_string(index=False))

    print("\n📊 RESUMO TOTAL:")
    print(f"   ➕ Total inseridos   : {total_inseridos}")
    print(f"   🔁 Total atualizados: {total_atualizados}")
    print(f"   ❌ Total ignorados  : {total_ignorados}")

    conn.close()

def leitor_codigo_barras():
    def verificar_codigo(codigo):
        codigo = codigo.lstrip("0")
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE serial = ?", (codigo,))
        resultado = cursor.fetchone()
        conn.close()
        if resultado:
            print(f"\n✅ Código encontrado: {codigo}")
            print(f"Item: {resultado[7]} | Máquina: {resultado[5]} | Quantidade: {resultado[9]} | Status: {resultado[10]}")
        else:
            print(f"\n❌ Código {codigo} não encontrado no banco.")

    root = tk.Tk()
    root.withdraw()
    print("\n🔎 Aguardando leitura de código de barras (pressione Cancelar para sair)...")
    while True:
        codigo = simpledialog.askstring("Leitor", "Escaneie o código de barras:")
        if codigo is None:
            break
        verificar_codigo(codigo)

# Execução principal
if __name__ == "__main__":
    criar_banco()
    importar_excels_para_sqlite()
    leitor_codigo_barras()
