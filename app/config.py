import os
import sys

def get_application_path():
    """Retorna o caminho base da aplicação, funcionando tanto em desenvolvimento quanto em produção"""
    if getattr(sys, 'frozen', False):
        # Se estiver executando como executável
        return os.path.dirname(sys.executable)
    else:
        # Se estiver executando em desenvolvimento
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = get_application_path()
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
EXCEL_DIR = os.path.join(DATA_DIR, 'excel_importados')
RELATORIOS_DIR = os.path.join(DATA_DIR, 'relatorios')
DB_PATH = os.path.join(DATA_DIR, 'dados.db')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)
os.makedirs(RELATORIOS_DIR, exist_ok=True)