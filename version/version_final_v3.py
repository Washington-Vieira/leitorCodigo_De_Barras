import os
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
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
            hora_leitura TIME  -- Nova coluna para o horário
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
    resumo_win = tk.Toplevel()
    resumo_win.title(f"Resumo - Status: {status}")
    resumo_win.geometry("1200x500")

    frame_top = tk.Frame(resumo_win)
    frame_top.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_top, text="Pesquisar:").pack(side="left")
    entry_search = tk.Entry(frame_top)
    entry_search.pack(side="left", padx=5)

    # Adicionar a coluna "Diferença de Dias"
    colunas = ("Pedido", "Data Pedido", "Máquina", "Item", "Status", "Qtd Programada", "Qtd Enviada", "Diferença", "Diferença de Dias")
    tree = ttk.Treeview(resumo_win, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=160)
    tree.pack(fill="both", expand=True)

    def carregar_dados(filtro=""):
        for i in tree.get_children():
            tree.delete(i)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        query = '''
            SELECT p.pedido, p.data_pedido, p.maquina, p.item, p.nome_status,
                   SUM(p.quantidade) as qtd_programada,
                   COALESCE((SELECT SUM(pp.quantidade) FROM produtos pp
                             JOIN leituras ll ON ll.serial = pp.serial
                             WHERE pp.pedido = p.pedido AND pp.maquina = p.maquina AND pp.item = p.item), 0) as qtd_enviada,
                   MAX(ll.data_leitura)
            FROM produtos p
            LEFT JOIN leituras ll ON p.serial = ll.serial
            WHERE p.nome_status = ?
            GROUP BY p.pedido, p.data_pedido, p.maquina, p.item, p.nome_status
        '''

        cursor.execute(query, (status,))
        for row in cursor.fetchall():
            pedido, data_pedido, maquina, item, status_val, qtd_prog, qtd_env, data_leitura = row

            # Calcular a diferença de dias
            if data_pedido and data_leitura:
                data_pedido_dt = datetime.strptime(data_pedido, '%d/%m/%Y')  # Corrigido o formato
                data_leitura_dt = datetime.strptime(data_leitura.split()[0], '%Y-%m-%d')  # Apenas a data
                diferenca_dias = (data_leitura_dt - data_pedido_dt).days
            else:
                diferenca_dias = "-"

            diff = qtd_prog - qtd_env
            if filtro.lower() in pedido.lower() or filtro.lower() in item.lower():
                tree.insert("", tk.END, values=(pedido, data_pedido, maquina, item, status_val, qtd_prog, qtd_env, diff, diferenca_dias))

        conn.close()

    def filtrar(*args):
        filtro = entry_search.get()
        carregar_dados(filtro)

    entry_search.bind("<KeyRelease>", filtrar)
    carregar_dados()

def verificar_codigo(event=None, entry_codigo=None, tree=None):
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
            data_pedido = resultado[2]
            linha_ato = resultado[6]
            item = resultado[7]
            maquina = resultado[5]
            quantidade = resultado[9]
            status = resultado[10]
            linha_lida = linha_ato[:4] if linha_ato else ''
            data_leitura = datetime.now().strftime('%Y-%m-%d')  # Apenas a data
            hora_leitura = datetime.now().strftime('%H:%M:%S')  # Apenas o horário

            # Calcular a diferença de dias
            data_pedido_dt = datetime.strptime(data_pedido, '%d/%m/%Y')  # Corrigido o formato
            data_leitura_dt = datetime.strptime(data_leitura, '%Y-%m-%d')
            diferenca_dias = (data_leitura_dt - data_pedido_dt).days

            # Converter data_leitura para o formato dd/mm/yyyy
            data_leitura_formatada = data_leitura_dt.strftime('%d/%m/%Y')

            cursor.execute('''
                INSERT INTO leituras (serial, pedido_lido, linha_lida, data_leitura, hora_leitura)
                VALUES (?, ?, ?, ?, ?)
            ''', (serial, pedido, linha_lida, data_leitura, hora_leitura))

            cursor.execute("SELECT SUM(quantidade) FROM produtos WHERE serial = ?", (serial,))
            qtd_enviada = cursor.fetchone()[0] or 0

            tree.insert("", tk.END, values=(pedido, data_pedido, serial, item, maquina, linha_lida, quantidade, qtd_enviada, status, f"{data_leitura_formatada} {hora_leitura}", diferenca_dias))
        else:
            print(f"⚠️ Código '{codigo}' já foi lido anteriormente.")
            messagebox.showwarning("Código já lido", f"⚠️ Código '{codigo}' já foi lido anteriormente.")
    else:
        print(f"❌ Código '{codigo}' não encontrado no banco de dados.")
        tree.insert("", tk.END, values=(codigo, "❌ Não encontrado", "-", "-", "-", "-", "-", "-", "-", "-", "-"))

    conn.commit()
    conn.close()

def leitor_codigo_barras_gui():
    root = tk.Tk()
    root.title("Leitor de Código de Barras")
    root.geometry("1200x500")

    top_frame = tk.Frame(root)
    top_frame.pack(pady=5)

    label = tk.Label(top_frame, text="Escaneie o código de barras:")
    label.pack(side="left")

    entry_codigo = tk.Entry(top_frame, font=("Arial", 14), width=40)
    entry_codigo.pack(side="left", padx=10)
    entry_codigo.focus()
    entry_codigo.bind("<Return>", lambda event: verificar_codigo(event, entry_codigo, tree))

    botao_pendente = tk.Button(top_frame, text="📋 Pendentes", command=lambda: abrir_resumo_status("PENDENTE"))
    botao_pendente.pack(side="left", padx=5)

    botao_andamento = tk.Button(top_frame, text="🔄 Em Andamento", command=lambda: abrir_resumo_status("EM ANDAMENTO"))
    botao_andamento.pack(side="left", padx=5)

    botao_concluido = tk.Button(top_frame, text="✅ Concluídos", command=lambda: abrir_resumo_status("CONCLUÍDO"))
    botao_concluido.pack(side="left", padx=5)

    # Adicionar a coluna "Hora Leitura"
    colunas = ("Pedido", "Data Pedido", "Serial", "Item", "Máquina", "Linha", "Qtd Programada", "Qtd Enviada", "Status", "Data/Hora Leitura", "Diferença de Dias")
    tree = ttk.Treeview(root, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(pady=10, fill="both", expand=True)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.pedido_lido, p.data_pedido, l.serial, p.item, p.maquina, l.linha_lida,
               p.quantidade, (SELECT SUM(pp.quantidade) FROM produtos pp WHERE pp.serial = l.serial),
               p.nome_status, l.data_leitura, l.hora_leitura  -- Incluímos hora_leitura
        FROM leituras l
        LEFT JOIN produtos p ON l.serial = p.serial
        ORDER BY l.data_leitura ASC
    ''')
    for row in cursor.fetchall():
        pedido, data_pedido, serial, item, maquina, linha_lida, quantidade, qtd_enviada, status, data_leitura, hora_leitura = row

        # Calcular a diferença de dias
        if data_pedido and data_leitura:
            data_pedido_dt = datetime.strptime(data_pedido, '%d/%m/%Y')  # Corrigido o formato
            data_leitura_dt = datetime.strptime(data_leitura.split()[0], '%Y-%m-%d')  # Apenas a data
            diferenca_dias = (data_leitura_dt - data_pedido_dt).days

            # Converter data_leitura para o formato dd/mm/yyyy
            data_leitura_formatada = data_leitura_dt.strftime('%d/%m/%Y')

            # Concatenar data_leitura_formatada com hora_leitura
            data_hora_leitura = f"{data_leitura_formatada} {hora_leitura}" if hora_leitura else data_leitura_formatada
        else:
            diferenca_dias = "-"
            data_hora_leitura = "-"

        tree.insert("", tk.END, values=(pedido, data_pedido, serial, item, maquina, linha_lida, quantidade, qtd_enviada, status, data_hora_leitura, diferenca_dias))
    conn.close()

    root.mainloop()

if __name__ == "__main__":
    criar_banco()
    importar_excels_para_sqlite()
    leitor_codigo_barras_gui()
