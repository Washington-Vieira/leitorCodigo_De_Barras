# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('app', 'app'), ('data', 'data'), ('monitor_importacao_v2.py', '.'), ('verificar_duplicatas.py', '.')]
datas += collect_data_files('tkinter')
datas += collect_data_files('tkcalendar')
datas += collect_data_files('PIL')
datas += collect_data_files('watchdog')


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=['pandas', 'openpyxl', 'watchdog', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'monitor_importacao_v2', 'verificar_duplicatas', 'sqlite3', 'shutil', 'threading', 'tkcalendar', 'datetime', 'PIL', 'PIL.Image', 'app.models.database', 'app.models.caixa', 'app.models.produto', 'app.models.leitura', 'app.models.codigo_nao_identificado', 'app.controllers.main_controller', 'app.controllers.resumo_controller', 'app.controllers.caixas_fechadas_controller', 'app.controllers.itens_sem_caixa_controller', 'app.controllers.codigos_nao_identificados_controller', 'app.views.main_view', 'app.views.resumo_view', 'app.views.caixas_fechadas_view', 'app.views.itens_sem_caixa_view', 'app.views.codigos_nao_identificados_view', 'app.views.caixa_dialog', 'app.views.selecionar_caixa_dialog', 'app.utils.excel_handler', 'app.utils.excel_importer', 'app.utils.db_checker'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LeitorCodigoBarras',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
