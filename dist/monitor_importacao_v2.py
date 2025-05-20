import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.utils.excel_importer import ExcelImporter

class ExcelMonitor(FileSystemEventHandler):
    def __init__(self):
        self.PASTA_EXCEL = 'data/excel_importados'
        self.excel_importer = ExcelImporter()

    def _processar_arquivo(self, arquivo):
        try:
            stats = self.excel_importer._processar_arquivo(arquivo)
            if stats:
                print(f"\n📊 Resumo da importação de {arquivo}:")
                print(f"   ➕ Inseridos   : {stats['inseridos']}")
                print(f"   ⏭️ Ignorados  : {stats['ignorados']}")
        except Exception as e:
            print(f"❌ Erro ao processar arquivo {arquivo}: {e}")

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.xlsx', '.xls')):
            arquivo = os.path.basename(event.src_path)
            print(f"\n📄 Novo arquivo detectado: {arquivo}")
            self._processar_arquivo(arquivo)

def iniciar_monitoramento():
    pasta_excel = 'data/excel_importados'
    if not os.path.exists(pasta_excel):
        os.makedirs(pasta_excel)
        print(f"📁 Pasta '{pasta_excel}' criada.")
    
    print(f"👀 Monitorando a pasta: {pasta_excel}")
    print("📌 Coloque seus arquivos Excel nesta pasta para importação automática")
    print("📋 Cada importação gerará um relatório detalhado na pasta 'data/relatorios'")
    
    event_handler = ExcelMonitor()
    observer = Observer()
    observer.schedule(event_handler, pasta_excel, recursive=False)
    observer.start()
    
    # Processar arquivos existentes
    arquivos_existentes = [f for f in os.listdir(pasta_excel) if f.endswith(('.xlsx', '.xls'))]
    if arquivos_existentes:
        print("\n⏳ Processando arquivos existentes...")
        for arquivo in arquivos_existentes:
            event_handler._processar_arquivo(arquivo)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n⚡ Monitoramento interrompido pelo usuário")
    
    observer.join()

if __name__ == "__main__":
    iniciar_monitoramento() 