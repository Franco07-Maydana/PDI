# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# IMPORTANTE:
# Agregamos módulos ocultos que PyInstaller NO detecta
hidden_imports = [
    "mysql.connector",
    "mysql.connector.plugins.mysql_native_password",
    "mysql.connector.locales.eng",
    "mysql.connector.locales.es",
]

a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ServidorStock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=True,   # Si querés ocultar la consola poné False
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
