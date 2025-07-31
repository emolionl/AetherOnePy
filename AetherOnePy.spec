# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
import sys
from PyInstaller.utils.hooks import get_package_paths

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

# --- FIX FOR pythonnet/pywebview ---
# Get the paths for clr_loader, pythonnet, and pywebview using PyInstaller's utility functions
print("=== Collecting pythonnet and clr_loader files ===")
try:
    clr_loader_path = get_package_paths('clr_loader')[1]
    pythonnet_path = get_package_paths('pythonnet')[1]
    webview_path = get_package_paths('webview')[1]
    
    print(f"clr_loader path: {clr_loader_path}")
    print(f"pythonnet path: {pythonnet_path}")
    print(f"pywebview path: {webview_path}")
    
    # Add the entire clr_loader and pythonnet directories to the bundle
    clr_loader_data = (clr_loader_path, "clr_loader")
    pythonnet_data = (pythonnet_path, "pythonnet")
    
    # Add the necessary webview files
    webview_dll = (os.path.join(webview_path, "platforms", "edgehtml.dll"), "webview/platforms")
    webview_host = (os.path.join(webview_path, "platforms", "webviewhost.exe"), "webview/platforms")
    
except Exception as e:
    print(f"Warning: Could not find package. The build might fail. Error: {e}")
    clr_loader_data = None
    pythonnet_data = None
    webview_dll = None
    webview_host = None

# Collect data files from the source tree
datas = [
    ('py', 'py'),
    ('data', 'data'),
    ('ui/dist/ui/browser', 'ui/dist/ui/browser')
]

if clr_loader_data:
    datas.append(clr_loader_data)
if pythonnet_data:
    datas.append(pythonnet_data)
if webview_dll:
    datas.append(webview_dll)
if webview_host:
    datas.append(webview_host)

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