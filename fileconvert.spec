# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec — FileConvert
====================================
Build: pyinstaller fileconvert.spec
Çıktı: dist/FileConvertPro/FileConvertPro.exe
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

datas = [
    ('assets', 'assets'),
    ('ui_qml/qml', 'ui_qml/qml'),
]
try:
    datas += collect_data_files('pdf2docx')
except Exception:
    pass

hiddenimports = [
    'win32com',
    'win32com.client',
    'fitz',
    'docx',
    'pytesseract',
    'PIL',
    'openpyxl',
    'odf',
    'PySide6.QtQuick',
    'PySide6.QtQml',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
]
hiddenimports += collect_submodules('core')
hiddenimports += collect_submodules('ui_qml')
try:
    hiddenimports += collect_submodules('pdf2docx')
except Exception:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FileConvertPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='assets/icons/app_icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='FileConvertPro',
)
