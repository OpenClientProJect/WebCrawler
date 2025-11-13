# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['FBver\\FBver.py'],
    pathex=[],
    binaries=[],
    datas=[('FBver\\image\\FB_it.ico', 'image'), ('FBver\\image\\loginBackground.png', 'image'), ('FBver\\image\\loginBackground.png', 'image'), ('FBver\\authorization.py', '.'), ('FBver\\AuthorizeManage.dll', '.'), ('FBver\\FB_loginwin.py', '.'), ('FBver\\FBmain.py', '.'), ('FBver\\FB_middle.py', '.'), ('FBver\\FB_status.py', '.'), ('FBver\\FB_lists.py', '.'), ('FBver\\FB_win.py', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6'],
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
    name='FBver',
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
    version='FBver\\file_version_info.txt',
    icon=['FBver\\image\\FB_it.ico'],
)
