import sqlite3
from datetime import datetime
from ..models.database import Database
from ..utils.excel_handler import ExcelHandler

class ResumoController:
    def __init__(self, status):
        self.status = status
        self.excel_handler = ExcelHandler()
        self.view = None

    def carregar_dados(self, filtro=""):
        conn = sqlite3.connect(Database.DB_NAME)
        cursor = conn.cursor()

        query = '''
            SELECT p.pedido, p.data_pedido, p.maquina, p.item, p.nome_status,
                   SUM(p.quantidade) as qtd_programada,
                   COALESCE((
                       SELECT SUM(pp.quantidade) 
                       FROM produtos pp
                       JOIN leituras ll ON ll.serial = pp.serial
                       WHERE pp.pedido = p.pedido 
                       AND pp.maquina = p.maquina 
                       AND pp.item = p.item
                   ), 0) as qtd_enviada,
                   MAX(ll.data_leitura)
            FROM produtos p
            LEFT JOIN leituras ll ON p.serial = ll.serial
            WHERE p.nome_status = ?
            GROUP BY p.pedido, p.data_pedido, p.maquina, p.item, p.nome_status
        '''

        cursor.execute(query, (self.status,))
        dados = cursor.fetchall()
        conn.close()
        return dados

    def filtrar_resumo(self, filtro):
        self.view.tree.delete(*self.view.tree.get_children())
        dados = self.carregar_dados()
        
        for row in dados:
            if filtro.lower() in str(row[0]).lower() or \
               filtro.lower() in str(row[3]).lower():
                self.inserir_linha(row)

    def inserir_linha(self, row):
        pedido, data_pedido, maquina, item, status, qtd_prog, qtd_env, data_leitura = row
        
        if data_pedido and data_leitura:
            data_pedido_dt = datetime.strptime(data_pedido, '%d/%m/%Y')
            data_leitura_dt = datetime.strptime(data_leitura.split()[0], '%Y-%m-%d')
            diferenca_dias = (data_leitura_dt - data_pedido_dt).days
        else:
            diferenca_dias = "-"

        diff = qtd_prog - qtd_env

        self.view.tree.insert("", "end", values=(
            pedido, data_pedido, maquina, item, status, 
            qtd_prog, qtd_env, diff, diferenca_dias
        ))

    def exportar_resumo(self, status):
        self.excel_handler.exportar_para_excel(
            self.view.tree, 
            f"resumo_{status.lower()}.xlsx"
        )