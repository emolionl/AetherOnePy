# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
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

# Collect data files from the source tree
datas = [
    ('py', 'py'),
    ('data', 'data'),
    ('ui/dist/ui/browser', 'ui/dist/ui/browser')
]

# Add pythonnet runtime files
try:
    import pythonnet
    import os
    pythonnet_path = os.path.dirname(pythonnet.__file__)
    runtime_path = os.path.join(pythonnet_path, 'runtime')
    if os.path.exists(runtime_path):
        datas.append((runtime_path, 'pythonnet/runtime'))
        print(f"Added pythonnet runtime files from: {runtime_path}")
    else:
        print(f"Warning: pythonnet runtime path not found: {runtime_path}")
except ImportError:
    print("Warning: pythonnet not available during build")

# Add qrcode module files to ensure proper inclusion
try:
    import qrcode
    qrcode_path = os.path.dirname(qrcode.__file__)
    datas.append((qrcode_path, 'qrcode'))
    print(f"Added qrcode module files from: {qrcode_path}")
except ImportError:
    print("Warning: qrcode not available during build")

excludes = [
    'matplotlib', 'scipy', 'opencv-python', 'cv2', 'pygame', 
    'sphinx', 'sphinx_rtd_theme', 'gitpython', 
    'git', 'eventlet', 'numpy', 'pandas', 'tkinter', 'test', 'unittest'
]

hiddenimports = [
    'flask', 'webview', 'screeninfo', 'subprocess', 'time', 'sys', 'os',
    'urllib.request', 'urllib.error', 'traceback', 'threading', 'shutil', 
    'queue', 'flask.templating', 'jinja2', 'werkzeug', 'flask_cors', 'flask_socketio',
    'pythonnet', 'clr', 'clr_loader', 'clr_loader.netfx', 'clr_loader.types',
    'qrcode', 'qrcode.constants', 'qrcode.image', 'qrcode.image.pil', 'qrcode.image.base',
    'flasgger', 'PIL', 'PIL.ImageDraw', 'PIL.ImageFont', 'dateutil', 'dateutil.parser',
    'psutil', 'asyncio', 'argparse', 'platform', 'socket', 're', 'json', 'logging',
    'importlib', 'multiprocessing', 'io',
    # Plugin dependencies from requirements.txt files
    'dotenv', 'requests', 'rich', 'rich.print', 'rich.pretty', 'icecream',
    # Core dependencies from setup.py
    'waitress', 'pyperclip', 'gitpython', 'openai',
    # Additional plugin imports
    'datetime', 'uuid', 'flasgger.swag_from'
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

# Verify critical modules are available
print("=== VERIFYING CRITICAL MODULES ===")
try:
    import qrcode
    print(f"✓ qrcode module available at: {qrcode.__file__}")
except ImportError as e:
    print(f"✗ qrcode module missing: {e}")

try:
    from PIL import Image
    print(f"✓ PIL module available")
except ImportError as e:
    print(f"✗ PIL module missing: {e}")