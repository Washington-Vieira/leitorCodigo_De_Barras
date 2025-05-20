import os
import shutil
import subprocess
import sys
import platform
from datetime import datetime

def criar_executavel():
    print("🚀 Iniciando criação do executável...")
    
    # Registrar data e hora do build
    data_build = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Criar pastas necessárias
    pastas = ['data/excel_importados', 'data/relatorios', 'data/backup', 'logs']
    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"📁 Pasta '{pasta}' criada")
    
    # Configurar comando PyInstaller
    comando = [
        'pyinstaller',
        '--name=LeitorCodigoBarras',
        '--onefile',
        '--windowed',
        '--noconsole',
        '--add-data=app;app',
        '--add-data=data;data',
        '--add-data=monitor_importacao_v2.py;.',
        '--add-data=verificar_duplicatas.py;.',
        '--paths=.',  # Adiciona o diretório atual ao PYTHONPATH
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=watchdog',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=monitor_importacao_v2',
        '--hidden-import=verificar_duplicatas',
        '--hidden-import=sqlite3',
        '--hidden-import=shutil',
        '--hidden-import=threading',
        '--hidden-import=tkcalendar',
        '--hidden-import=datetime',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--collect-data=tkinter',
        '--collect-data=tkcalendar',
        '--collect-data=PIL',
        '--collect-data=watchdog',
        '--hidden-import=app.models.database',
        '--hidden-import=app.models.caixa',
        '--hidden-import=app.models.produto',
        '--hidden-import=app.models.leitura',
        '--hidden-import=app.models.codigo_nao_identificado',
        '--hidden-import=app.controllers.main_controller',
        '--hidden-import=app.controllers.resumo_controller',
        '--hidden-import=app.controllers.caixas_fechadas_controller',
        '--hidden-import=app.controllers.itens_sem_caixa_controller',
        '--hidden-import=app.controllers.codigos_nao_identificados_controller',
        '--hidden-import=app.views.main_view',
        '--hidden-import=app.views.resumo_view',
        '--hidden-import=app.views.caixas_fechadas_view',
        '--hidden-import=app.views.itens_sem_caixa_view',
        '--hidden-import=app.views.codigos_nao_identificados_view',
        '--hidden-import=app.views.caixa_dialog',
        '--hidden-import=app.views.selecionar_caixa_dialog',
        '--hidden-import=app.utils.excel_handler',
        '--hidden-import=app.utils.excel_importer',
        '--hidden-import=app.utils.db_checker',
        '--log-level=DEBUG',  # Aumentar nível de log para debug
        '--clean',
        'main.py'
    ]
    
    try:
        # Verificar sistema operacional
        sistema = platform.system()
        print(f"\n💻 Sistema Operacional detectado: {sistema}")
        
        # Verificar e criar diretórios necessários
        print("\n📁 Verificando diretórios necessários...")
        diretorios_necessarios = [
            'data/excel_importados',
            'data/relatorios',
            'data/backup',
            'logs',
            'app/assets'  # Adicionado assets
        ]
        for pasta in diretorios_necessarios:
            if not os.path.exists(pasta):
                os.makedirs(pasta)
                print(f"✅ Pasta '{pasta}' criada")
            else:
                print(f"✓ Pasta '{pasta}' já existe")
        
        # Verificar se o ícone existe e é válido
        icon_path = 'app/assets/icon.ico'
        icon_valido = False
        if os.path.exists(icon_path):
            try:
                from PIL import Image
                Image.open(icon_path)
                comando.append(f'--icon={icon_path}')
                icon_valido = True
                print("✅ Ícone encontrado e válido")
            except Exception as e:
                print(f"⚠️ Erro ao validar ícone: {str(e)}")
                print("⚠️ Continuando build sem ícone")
        else:
            print("⚠️ Arquivo de ícone não encontrado - continuando sem ícone")
        
        # Verificar e instalar dependências necessárias
        dependencias = {
            'tkcalendar': '1.6.1',
            'pandas': '2.1.0',
            'openpyxl': '3.1.2',
            'watchdog': '3.0.0',
            'pyinstaller': '6.13.0',  # Versão mais recente compatível
            'pillow': '11.2.1',  # Atualizado para versão compatível
            'xlsxwriter': '3.2.0',
            'unicodedata2': '15.1.0',
            'pywin32': '310',  # Atualizado para versão mais recente
            'psutil': '5.9.8',
            'python-dateutil': '2.8.2'
        }
        
        print("\n📦 Verificando dependências...")
        for pacote, versao in dependencias.items():
            try:
                if pacote == 'sqlite3':
                    continue  # sqlite3 é parte do Python padrão
                __import__(pacote)
                print(f"✅ {pacote} já instalado")
            except ImportError:
                print(f"⚠️ Instalando {pacote} {versao}...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", f"{pacote}=={versao}"], check=True)
                    print(f"✅ {pacote} instalado com sucesso!")
                except subprocess.CalledProcessError:
                    print(f"⚠️ Tentando instalar versão mais recente de {pacote}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", pacote], check=True)
                    print(f"✅ {pacote} instalado com sucesso!")
        
        # Criar requirements.txt
        print("\n📝 Gerando requirements.txt...")
        with open('requirements.txt', 'w') as f:
            for pacote, versao in dependencias.items():
                f.write(f"{pacote}=={versao}\n")
        print("✅ requirements.txt criado com sucesso!")
        
        # Limpar diretórios anteriores
        print("\n🧹 Limpando builds anteriores...")
        for pasta in ['build', 'dist']:
            if os.path.exists(pasta):
                shutil.rmtree(pasta)
                print(f"   Pasta '{pasta}' removida")
        
        # Executar PyInstaller
        print("\n🛠️ Criando executável...")
        try:
            subprocess.run(comando, check=True)
            print("✅ Executável criado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar executável: {e}")
            with open('build_error.log', 'w', encoding='utf-8') as f:
                f.write(f'Erro ocorrido em: {data_build}\n')
                f.write(f'Erro: {str(e)}\n')
            print("Log de erro salvo em build_error.log")
            sys.exit(1)
        
        # Copiar arquivos adicionais
        if os.path.exists('dist'):
            print("\n📦 Copiando arquivos adicionais...")
            for pasta in ['data/excel_importados', 'data/relatorios', 'data/backup', 'logs']:
                destino = os.path.join('dist', pasta)
                if not os.path.exists(destino):
                    os.makedirs(destino)
                    print(f"✅ Pasta '{pasta}' criada em dist/")
            
            # Copiar arquivos necessários
            arquivos = [
                'monitor_importacao_v2.py',
                'verificar_duplicatas.py',
                'README.md',
                'requirements.txt'
            ]
            for arquivo in arquivos:
                if os.path.exists(arquivo):
                    shutil.copy2(arquivo, os.path.join('dist', arquivo))
                    print(f"✅ Arquivo '{arquivo}' copiado para dist/")
            
            # Criar arquivo version.txt com a versão atual e informações do build
            with open(os.path.join('dist', 'version.txt'), 'w') as f:
                f.write('Versão: 1.3.1\n')
                f.write(f'Data do Build: {data_build}\n')
                f.write(f'Sistema Operacional: {sistema}\n')
                f.write(f'Python: {sys.version}\n')
            print("📝 Arquivo version.txt criado com informações detalhadas")
            
            # Criar arquivo de log do build
            with open(os.path.join('dist', 'logs', 'build_log.txt'), 'w') as f:
                f.write(f'Build realizado em: {data_build}\n')
                f.write(f'Sistema Operacional: {sistema}\n')
                f.write(f'Python: {sys.version}\n')
                f.write('\nDependências instaladas:\n')
                for pacote, versao in dependencias.items():
                    f.write(f'- {pacote}: {versao}\n')
                f.write('\nNovas funcionalidades na versão 1.3.1:\n')
                f.write('- Melhorias na importação de planilhas\n')
                f.write('- Otimização no feedback de importação\n')
                f.write('- Correção na exclusão em massa de códigos\n')
                f.write('- Melhorias na atualização de interfaces\n')
                f.write('- Correção na atualização de totais nas caixas\n')
                f.write('- Melhorias na sincronização entre telas\n')
                f.write('- Otimização no processamento de códigos não identificados\n')
            print("📝 Log do build criado")
        
        print("\n✨ Build concluído com sucesso!")
        print("\nO executável está disponível em:")
        print("  dist/LeitorCodigoBarras.exe")
        
        # Compilar o instalador simples
        print("\n🔧 Compilando instalador simples...")
        comando_instalador = [
            'pyinstaller',
            '--name=Instalador_LeitorCodigoBarras',
            '--onefile',
            '--windowed',
            '--noconsole',
            '--clean'
        ]

        # Verificar se o diretório assets existe e tem conteúdo
        if os.path.exists('app/assets') and os.listdir('app/assets'):
            comando_instalador.append('--add-data=app/assets;app/assets')
            print("✓ Diretório assets encontrado e será incluído no build")
        else:
            print("⚠️ Diretório assets vazio ou não encontrado - continuando sem assets")

        # Adicionar imports necessários
        comando_instalador.extend([
            '--hidden-import=tkinter',
            '--hidden-import=tkinter.ttk',
            '--hidden-import=tkinter.messagebox',
            '--hidden-import=tkinter.filedialog',
            '--hidden-import=win32com.client',
            '--hidden-import=pythoncom',
            'instalador_simples.py'
        ])
        
        # Só adiciona o ícone se ele foi validado anteriormente
        if icon_valido:
            comando_instalador.append(f'--icon={icon_path}')
        
        try:
            subprocess.run(comando_instalador, check=True)
            print("✅ Instalador simples compilado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Erro ao compilar instalador simples: {str(e)}")
            print("Continuando com o resto do processo...")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        with open('build_error.log', 'w') as f:
            f.write(f'Erro ocorrido em: {data_build}\n')
            f.write(f'Erro: {str(e)}\n')
        print("Log de erro salvo em build_error.log")
        sys.exit(1)

if __name__ == "__main__":
    criar_executavel() 