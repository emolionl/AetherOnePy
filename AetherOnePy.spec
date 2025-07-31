# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
import sys
import site

# Clean up old build files automatically
print("=== CLEANUP OLD FILES ===")
try:
    if os.path.exists('dist'):
        print("Removing old dist directory...")
        # Force remove with retries
        for i in range(3):
            try:
                shutil.rmtree('dist')
                break
            except PermissionError:
                if i < 2:  # Retry up to 3 times
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

# CREATE BUILD DIRECTORIES AFTER CLEANUP
print("=== CREATING BUILD DIRECTORIES ===")
try:
    os.makedirs('build', exist_ok=True)
    os.makedirs('build/AetherOnePy', exist_ok=True)
    print("Build directories created")
except Exception as e:
    print(f"Directory creation error: {e}")

# Function to collect all data files with correct path mapping
def collect_data_files():
    datas = []
    
    # Collect py directory and all its contents
    if os.path.exists('py'):
        datas.append(('py', 'py'))
        print("Collected py directory")
    
    # --- NEW: Check for and collect plugins from site-packages ---
    # List the known plugin package names
    plugin_packages = [
        'AetherOnePySocialPlugin',
        'FinCompassPlugin'
    ]
    
    print("Looking for plugins in Python site-packages...")
    # Get the path to the site-packages directory
    site_packages_path = next(p for p in site.getsitepackages() if 'site-packages' in p)
    
    for plugin_name in plugin_packages:
        plugin_src_path = os.path.join(site_packages_path, plugin_name)
        plugin_dest_path = os.path.join('py', 'plugins', plugin_name)
        if os.path.exists(plugin_src_path):
            datas.append((plugin_src_path, plugin_dest_path))
            print(f" - Found and collected plugin: {plugin_name}")
        else:
            print(f" - Warning: Plugin directory not found: {plugin_name}")
    # ----------------------------------------------------------------------
    
    # Collect data directory and all its contents
    if os.path.exists('data'):
        datas.append(('data', 'data'))
        print("Collected data directory")
    
    # Collect UI files and preserve their directory structure exactly
    ui_path = 'ui/dist/ui/browser'
    if os.path.exists(ui_path):
        datas.append((ui_path, ui_path))
        print(f"Collected UI files from {ui_path}")
    else:
        print(f"Warning: UI directory not found at {ui_path}. The UI might be missing.")
    
    # Explicitly collect pythonnet and clr_loader dependencies
    if os.path.exists('pythonnet'):
        datas.append(('pythonnet', 'pythonnet'))
        print("Collected pythonnet dependencies")
    
    if os.path.exists('clr_loader'):
        datas.append(('clr_loader', 'clr_loader'))
        print("Collected clr_loader dependencies")
    
    return datas

# Call the function to populate the datas list
datas = collect_data_files()

# Add exclusions for faster build
excludes = [
    'matplotlib', 'scipy', 'opencv-python', 'cv2', 'pygame', 
    'PIL', 'Pillow', 'sphinx', 'sphinx_rtd_theme', 'gitpython', 
    'git', 'eventlet', 'numpy', 'pandas', 'tkinter', 'test', 'unittest'
]

# Hidden imports
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