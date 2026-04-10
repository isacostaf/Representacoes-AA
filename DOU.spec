# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata


hiddenimports = []
hiddenimports += collect_submodules('streamlit')
hiddenimports += collect_submodules('streamlit.web')
hiddenimports += collect_submodules('webview')
hiddenimports += collect_submodules('selenium')
hiddenimports += collect_submodules('webdriver_manager')

datas = []
datas += collect_data_files('streamlit')
datas += collect_data_files('webdriver_manager')
datas += copy_metadata('streamlit')
datas += copy_metadata('pandas')
datas += copy_metadata('selenium')
datas += copy_metadata('webdriver_manager')
datas += [
    ('app.py', '.'),
    ('analise.py', '.'),
    ('linkbusca.py', '.'),
    ('gerar_relatorio.py', '.'),
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='DOU',
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
