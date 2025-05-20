import os
import sys
import threading
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Database
from app.views.main_view import MainView
from app.controllers.main_controller import MainController
from app.config import EXCEL_DIR
from monitor_importacao_v2 import iniciar_monitoramento
from app.utils.db_checker import verificar_duplicatas, limpar_duplicatas, adicionar_restricoes

def verificar_integridade_banco():
    print("\n🔍 Verificando integridade do banco de dados...")
    duplicatas = verificar_duplicatas()
    
    if not duplicatas['produtos'] and not duplicatas['leituras']:
        print("✅ Não foram encontradas duplicatas no banco de dados!")
        return True
        
    print("\n⚠️ Atenção: Foram encontradas duplicatas!")
    
    if duplicatas['produtos']:
        print("\nDuplicatas na tabela produtos:")
        for dup in duplicatas['produtos']:
            print(f"Serial: {dup[0]}, Máquina: {dup[1]}, Quantidade: {dup[2]}")
    
    if duplicatas['leituras']:
        print("\nDuplicatas na tabela leituras:")
        for dup in duplicatas['leituras']:
            print(f"Serial: {dup[0]}, Pedido: {dup[1]}, Linha: {dup[2]}")
    
    print("\n🔄 Removendo duplicatas automaticamente...")
    limpar_duplicatas()
    print("✅ Duplicatas removidas com sucesso!")
    
    print("\n🔒 Adicionando restrições para prevenir futuras duplicatas...")
    adicionar_restricoes()
    print("✅ Restrições adicionadas com sucesso!")
    return True

def inicializar_banco():
    """Inicializa o banco de dados com suas tabelas"""
    print("\n🔧 Inicializando banco de dados...")
    try:
        Database.criar_banco()
        print("✅ Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {str(e)}")
        return False

def main():
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Leitor de Código de Barras')
    parser.add_argument('--init-db', action='store_true', help='Inicializa o banco de dados')
    parser.add_argument('--check-db', action='store_true', help='Verifica a integridade do banco de dados')
    args = parser.parse_args()

    # Se solicitado, apenas inicializar o banco e sair
    if args.init_db:
        success = inicializar_banco()
        sys.exit(0 if success else 1)

    # Se solicitado, apenas verificar o banco e sair
    if args.check_db:
        success = verificar_integridade_banco()
        sys.exit(0 if success else 1)

    # Criar banco de dados se não existir
    Database.criar_banco()
    
    # Verificar duplicatas
    if not verificar_integridade_banco():
        print("❌ Erro ao verificar integridade do banco. O sistema será encerrado.")
        return
    
    # Iniciar thread de monitoramento
    monitor_thread = threading.Thread(target=iniciar_monitoramento, daemon=True)
    monitor_thread.start()
    
    # Inicializar controlador
    controller = MainController()
    
    # Inicializar view e configurar referência no controlador
    view = MainView(controller)
    controller.view = view
    
    # Importar dados e inicializar após a view estar pronta
    controller.inicializar()
    
    # Atualizar a tabela após a inicialização
    view.atualizar_tabela()
    
    # Iniciar a aplicação
    view.root.mainloop()

if __name__ == "__main__":
    main()