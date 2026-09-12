# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec — FileConvert Pro
====================================
Build: pyinstaller fileconvert.spec
Çıktı: dist/FileConvertPro/FileConvertPro.exe

--onedir modu kullanılır (--onefile değil): PyInstaller'ın --onefile
modu her başlangıçta kendini geçici bir dizine açar; bu, LibreOffice/
MS Office subprocess çağrılarıyla (bkz. docs/wiki/libreoffice-motoru.md)
olası geçici-dizin çakışmalarını önlemek için --onedir tercih edildi.

.exe simgesi için ayrı bir .ico dosyası şimdilik yok (mevcut varlıklar
yalnızca .svg/.png) — bkz. docs/wiki/paketleme.md.
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='FileConvertPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    upx=True,
    upx_exclude=[],
    name='FileConvertPro',
)
