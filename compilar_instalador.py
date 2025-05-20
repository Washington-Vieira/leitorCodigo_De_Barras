import os
import subprocess
import sys
from datetime import datetime

def compilar_instalador():
    print("\n🚀 Iniciando compilação do instalador...")
    
    # Verificar dependências
    dependencias = {
        'pyinstaller': '6.13.0',
        'pywin32': '306',
        'pillow': '10.2.0'
    }
    
    print("\n📦 Verificando dependências...")
    for pacote, versao in dependencias.items():
        try:
            __import__(pacote)
            print(f"✅ {pacote} já instalado")
        except ImportError:
            print(f"⚠️ Instalando {pacote} {versao}...")
            subprocess.run([sys.executable, "-m", "pip", "install", f"{pacote}=={versao}"], check=True)
    
    # Configurar comando PyInstaller
    comando = [
        'pyinstaller',
        '--name=Instalador_LeitorCodigoBarras',
        '--onefile',
        '--windowed',
        '--clean',
        '--add-data=app/assets;app/assets',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=win32com.client',
        '--hidden-import=pythoncom',
        'instalador_simples.py'
    ]
    
    # Verificar ícone
    if os.path.exists('app/assets/icon.ico'):
        comando.append('--icon=app/assets/icon.ico')
    
    try:
        print("\n🛠️ Compilando instalador...")
        subprocess.run(comando, check=True)
        
        print("\n📝 Criando arquivo de informações...")
        with open('dist/version.txt', 'w') as f:
            f.write(f'Data de Compilação: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('Versão: 1.3.1\n')
            f.write('Tipo: Instalador Simples (Sem privilégios administrativos)\n')
        
        print("\n✨ Instalador compilado com sucesso!")
        print("\nO instalador está disponível em:")
        print(f"  dist/Instalador_LeitorCodigoBarras.exe")
        
    except Exception as e:
        print(f"\n❌ Erro ao compilar instalador: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    compilar_instalador() 