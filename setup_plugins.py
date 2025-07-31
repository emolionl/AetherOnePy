#!/usr/bin/env python3
"""
Local development plugin setup script
Use this to set up plugins in your local development environment
Works with your existing py/setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Setup plugins for local development"""
    print("🔧 Setting up AetherOnePy plugins for local development...")
    
    # Check if plugin manager exists
    if not os.path.exists("plugin_manager.py"):
        print("❌ plugin_manager.py not found. Make sure you're in the project root.")
        sys.exit(1)
    
    # Check if config exists
    if not os.path.exists("plugins-config.json"):
        print("❌ plugins-config.json not found. Make sure you're in the project root.")
        sys.exit(1)
    
    try:
        # Step 1: Install base dependencies with existing setup.py
        print("\n📦 Step 1: Installing base dependencies...")
        if os.path.exists("py/setup.py"):
            print("Using existing py/setup.py for base dependencies...")
            result = subprocess.run([
                sys.executable, "-c", 
                "import os; os.chdir('py'); exec(open('setup.py').read())"
            ], check=True)
            print("✅ Base dependencies installed!")
        else:
            print("⚠️ py/setup.py not found, installing minimal dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "flask", "flask-cors", "flask-socketio", "pywebview", "screeninfo"
            ], check=True)
        
        # Step 2: Download plugins
        print("\n🔌 Step 2: Downloading and installing plugins...")
        result = subprocess.run([
            sys.executable, "plugin_manager.py", 
            "--environment", "development",
            "--action", "install"
        ], check=True)
        
        # Step 3: Install plugin dependencies using setup.py again
        print("\n📦 Step 3: Installing plugin dependencies...")
        if os.path.exists("py/setup.py"):
            print("Running py/setup.py again to install plugin requirements...")
            result = subprocess.run([
                sys.executable, "-c", 
                "import os; os.chdir('py'); exec(open('setup.py').read())"
            ], check=True)
            print("✅ Plugin dependencies installed!")
        
        print("\n🎉 Plugin setup completed successfully!")
        print("\n📋 What was installed:")
        print("  ✅ Base AetherOnePy dependencies (via py/setup.py)")
        print("  ✅ All development plugins (via plugin manager)")
        print("  ✅ Plugin-specific requirements (via py/setup.py)")
        
        print("\n📋 To see installed plugins, run:")
        print("  python plugin_manager.py --action list")
        
        print("\n🚀 You can now run:")
        print("  cd py && python main.py --port 7000")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed with exit code {e.returncode}")
        print("💡 Try running individual steps manually:")
        print("   1. cd py && python setup.py")
        print("   2. python plugin_manager.py --environment development --action install") 
        print("   3. cd py && python setup.py  # (again for plugin deps)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()