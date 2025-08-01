# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
import subprocess
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

print("=== RUNNING SETUP.PY TO INSTALL ALL DEPENDENCIES ===")
try:
    import sys
    import subprocess
    
    # Change to py directory and run setup.py
    setup_script = os.path.join('py', 'setup.py')
    if os.path.exists(setup_script):
        print("Running py/setup.py to install all dependencies...")
        result = subprocess.run([sys.executable, setup_script], 
                              cwd='py', 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("[OK] setup.py completed successfully")
            if result.stdout:
                print("Setup output:", result.stdout)
        else:
            print(f"[WARNING] setup.py returned code {result.returncode}")
            if result.stderr:
                print("Setup errors:", result.stderr)
    else:
        print(f"[WARNING] setup.py not found at {setup_script}")
        
except Exception as e:
    print(f"[ERROR] Failed to run setup.py: {e}")

# Collect data files from the source tree
datas = [
    ('py', 'py'),
    ('data', 'data'),
    ('ui/dist/ui/browser', 'ui/dist/ui/browser')
]

# Add pythonnet runtime files manually
try:
    import pythonnet
    import os
    pythonnet_path = os.path.dirname(pythonnet.__file__)
    runtime_path = os.path.join(pythonnet_path, 'runtime')
    if os.path.exists(runtime_path):
        # Add entire runtime directory
        datas.append((runtime_path, 'pythonnet/runtime'))
        print(f"Added pythonnet runtime files from: {runtime_path}")
        
        # Manually add critical DLL files to binaries for better inclusion
        dll_files = [
            'Python.Runtime.dll',
            'Python.Runtime.Native.dll',
            'clrmodule.dll'
        ]
        
        for dll in dll_files:
            dll_path = os.path.join(runtime_path, dll)
            if os.path.exists(dll_path):
                # Add to binaries for direct inclusion
                if 'binaries' not in locals():
                    binaries = []
                binaries.append((dll_path, '.'))
                print(f"Added pythonnet DLL: {dll}")
            else:
                print(f"Warning: {dll} not found at {dll_path}")
    else:
        print(f"Warning: pythonnet runtime path not found: {runtime_path}")
except ImportError:
    print("Warning: pythonnet not available during build")

# Initialize binaries list if not already done
if 'binaries' not in locals():
    binaries = []


# Use the same logic as py/setup.py to discover plugin requirements
def get_plugin_requirements_like_setup():
    """Mirror the install_plugin_requirements() logic from py/setup.py"""
    plugin_imports = []
    plugins_dir = 'py/plugins'
    
    print("=== USING SETUP.PY LOGIC FOR PLUGIN DISCOVERY ===")
    
    if not os.path.isdir(plugins_dir):
        print(f"No plugins directory found at {plugins_dir}")
        return []
        
    for plugin_name in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, plugin_name)
        if os.path.isdir(plugin_path):
            req_path = os.path.join(plugin_path, 'requirements.txt')
            if os.path.exists(req_path):
                print(f"[PLUGIN-BUILD] Processing requirements for plugin: {plugin_name}")
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Clean package name (remove version specifiers)
                                pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0].split('[')[0]
                                pkg_name = pkg_name.strip()
                                
                                # Map pip package names to import names
                                import_mapping = {
                                    'python-dateutil': 'dateutil',
                                    'python-dotenv': 'dotenv', 
                                    'pillow': 'PIL',
                                    'pyjwt': 'jwt',
                                    'beautifulsoup4': 'bs4',
                                    'pyyaml': 'yaml'
                                }
                                
                                import_name = import_mapping.get(pkg_name.lower(), pkg_name)
                                
                                if import_name not in plugin_imports:
                                    plugin_imports.append(import_name)
                                    print(f"  -> {import_name}")
                                    
                                    # Add common submodules for critical packages
                                    if import_name == 'qrcode':
                                        submodules = ['qrcode.constants', 'qrcode.image', 'qrcode.image.pil', 'qrcode.image.base']
                                        plugin_imports.extend(submodules)
                                    elif import_name == 'rich':
                                        submodules = ['rich.print', 'rich.pretty', 'rich.console']
                                        plugin_imports.extend(submodules) 
                                    elif import_name == 'PIL':
                                        submodules = ['PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont']
                                        plugin_imports.extend(submodules)
                                    elif import_name == 'flasgger':
                                        plugin_imports.append('flasgger.swag_from')
                                    elif import_name == 'dateutil':
                                        plugin_imports.append('dateutil.parser')
                                        
                except Exception as e:
                    print(f"[PLUGIN-BUILD] Failed to process requirements for {plugin_name}: {e}")
            else:
                print(f"[PLUGIN-BUILD] No requirements.txt for plugin: {plugin_name}")
    
    print(f"[PLUGIN-BUILD] Total plugin dependencies: {len(plugin_imports)}")
    return plugin_imports

# Get dynamic plugin requirements using setup.py logic
plugin_hiddenimports = get_plugin_requirements_like_setup()

excludes = [
    'matplotlib', 'scipy', 'opencv-python', 'cv2', 'pygame', 
    'sphinx', 'sphinx_rtd_theme', 'gitpython', 
    'git', 'eventlet', 'numpy', 'pandas', 'tkinter', 'test', 'unittest'
]

# Base hiddenimports (core + main app requirements)
base_hiddenimports = [
    'flask', 'webview', 'screeninfo', 'subprocess', 'time', 'sys', 'os',
    'urllib.request', 'urllib.error', 'traceback', 'threading', 'shutil', 
    'queue', 'flask.templating', 'jinja2', 'werkzeug', 'flask_cors', 'flask_socketio',
    'pythonnet', 'clr', 'clr_loader', 'clr_loader.netfx', 'clr_loader.types',
    'qrcode', 'qrcode.constants', 'qrcode.image', 'qrcode.image.pil', 'qrcode.image.base',
    'flasgger', 'PIL', 'PIL.ImageDraw', 'PIL.ImageFont', 'dateutil', 'dateutil.parser',
    'psutil', 'asyncio', 'argparse', 'platform', 'socket', 're', 'json', 'logging',
    'importlib', 'multiprocessing', 'io',
    # Core dependencies from setup.py (always installed)
    'requests', 'waitress', 'pyperclip', 'gitpython', 'openai',
    # Common additional imports
    'datetime', 'uuid', 'flasgger.swag_from'
]

# Dynamically add plugin requirements (mirrors py/setup.py behavior)
hiddenimports = base_hiddenimports + plugin_hiddenimports

# Remove duplicates while preserving order
seen = set()
hiddenimports = [x for x in hiddenimports if not (x in seen or seen.add(x))]

print(f"=== HIDDENIMPORTS SUMMARY ===")
print(f"Base imports: {len(base_hiddenimports)}")
print(f"Plugin imports added: {len(plugin_hiddenimports)}")
print(f"Total after deduplication: {len(hiddenimports)}")
if plugin_hiddenimports:
    print(f"Dynamic plugin imports: {plugin_hiddenimports}")

a = Analysis(
    ['desktop_launcher.py'],
    pathex=[],
    binaries=binaries,
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
    print(f"[OK] qrcode module available at: {qrcode.__file__}")
except ImportError as e:
    print(f"[ERROR] qrcode module missing: {e}")
    print("[INFO] This is expected if qrcode wasn't installed by setup.py yet")

try:
    from PIL import Image
    print(f"[OK] PIL module available")
except ImportError as e:
    try:
        import PIL
        print(f"[OK] PIL module available (via import PIL)")
    except ImportError:
        print(f"[ERROR] PIL/Pillow module missing: {e}")
        print("[INFO] This is expected if Pillow wasn't installed by setup.py yet")