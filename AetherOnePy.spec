# -*- mode: python ; coding: utf-8 -*-

import os
import shutil

print("=== CLEANUP OLD FILES ===")
try:
    if os.path.exists('dist'):
        print("Removing old dist directory...")
        for i in range(3):
            try:
                shutil.rmtree('dist')
                break
            except PermissionError:
                if i < 2:
                    import time
                    time.sleep(2)
                    continue
                else:
                    print("Warning: Could not remove dist directory completely")
    
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

def collect_data_files():
    datas = []
    
    # Collect the main py directory files
    if os.path.exists('py'):
        datas.append(('py', 'py'))
        print("Collected py directory")

    # Explicitly collect the plugins directory as a separate entry for safety
    plugins_path = 'py/plugins'
    if os.path.exists(plugins_path):
        datas.append((plugins_path, 'py/plugins'))
        print(f"Collected plugins directory from {plugins_path}")
    
    # Collect data directory and all its contents
    if os.path.exists('data'):
        datas.append(('data', 'data'))
        print("Collected data directory")
    
    # Collect UI files
    ui_path = 'ui/dist/ui/browser'
    if os.path.exists(ui_path):
        datas.append((ui_path, ui_path))
        print(f"Collected UI files from {ui_path}")
    else:
        print(f"Warning: UI directory not found at {ui_path}. The UI might be missing.")
    
    return datas

datas = collect_data_files()

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