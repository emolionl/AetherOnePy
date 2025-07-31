# -*- mode: python ; coding: utf-8 -*-

import os
import shutil

# This spec file now assumes the CI workflow has correctly placed all files
# into the py/ and data/ directories prior to the build.

print("=== CLEANUP OLD FILES ===")
try:
    if os.path.exists('dist'):
        print("Removing old dist directory...")
        shutil.rmtree('dist')
    if os.path.exists('build'):
        print("Removing old build directory...")
        shutil.rmtree('build')
    print("Cleanup completed")
except Exception as e:
    print(f"Cleanup warning: {e}")

print("=== CREATING BUILD DIRECTORIES ===")
try:
    os.makedirs('build', exist_ok=True)
    os.makedirs('build/AetherOnePy', exist_ok=True)
    print("Build directories created")
except Exception as e:
    print(f"Directory creation error: {e}")

# Collect data files from the source tree
datas = [
    ('py', 'py'),
    ('data', 'data'),
    ('ui/dist/ui/browser', 'ui/dist/ui/browser')
]

excludes = [
    'matplotlib', 'scipy', 'opencv-python', 'cv2', 'pygame', 
    'PIL', 'Pillow', 'sphinx', 'sphinx_rtd_theme', 'gitpython', 
    'git', 'eventlet', 'numpy', 'pandas', 'tkinter', 'test', 'unittest'
]

hiddenimports = [
    'flask', 'webview', 'screeninfo', 'subprocess', 'time', 'sys', 'os',
    'urllib.request', 'urllib.error', 'traceback', 'threading', 'shutil', 
    'queue', 'flask.templating', 'jinja2', 'werkzeug', 'flask_cors', 'flask_socketio',
    'pythonnet', 'clr_loader'
]

a = Analysis(
    ['desktop_launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AetherOnePy',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AetherOnePy',
)

print("=== BUILD COMPLETE ===")
print("Executable will be at: dist/AetherOnePy/AetherOnePy.exe")