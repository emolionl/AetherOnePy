# AetherOnePy Plugin Management System - Setup Guide

This document provides **step-by-step instructions** for setting up the automatic plugin management system for AetherOnePy.

## 🚀 Quick Start (TL;DR)

1. **Create the files** (see File Setup section below)
2. **Run locally**: `python setup_plugins.py` 
3. **Push to GitHub**: Plugins automatically included in builds
4. **Done!** 🎉

---

## 📋 Complete Setup Instructions

### Step 1: Create Required Files

Create these **5 new files** in your AetherOnePy project:

#### 1.1 Create Directory Structure
```bash
# Windows (PowerShell)
New-Item -ItemType Directory -Path ".github\workflows" -Force

# Linux/Mac (Bash)  
mkdir -p .github/workflows
```

#### 1.2 Create Plugin Configuration
**File:** `plugins-config.json` (in project root)

```json
{
  "plugins": {
    "AetherOnePySocialPlugin": {
      "name": "AetherOne Social Plugin",
      "description": "Social features and community integration for AetherOnePy",
      "version": "1.0.0",
      "author": "Isuret Polos",
      "repository": {
        "type": "github",
        "url": "https://github.com/isuretpolos/AetherOnePySocialPlugin.git",
        "branch": "main"
      },
      "enabled": true,
      "required": false,
      "dependencies": {
        "python": ["requests", "sqlite3"],
        "system": []
      },
      "install_path": "py/plugins/AetherOnePySocialPlugin"
    },
    "FinCompassPlugin": {
      "name": "Financial Compass Plugin", 
      "description": "Financial analysis and planning tools",
      "version": "2.1.0",
      "author": "Isuret Polos",
      "repository": {
        "type": "github",
        "url": "https://github.com/isuretpolos/FinCompassPlugin.git",
        "branch": "main"
      },
      "enabled": true,
      "required": false,
      "dependencies": {
        "python": ["pandas", "numpy", "matplotlib"],
        "system": []
      },
      "install_path": "py/plugins/FinCompassPlugin"
    }
  },
  "config": {
    "plugin_directory": "py/plugins",
    "data_directory": "data", 
    "auto_update": true,
    "verify_integrity": true,
    "parallel_downloads": 3,
    "timeout_seconds": 300
  },
  "environments": {
    "development": {
      "include_dev_plugins": true,
      "use_dev_branches": true
    },
    "production": {
      "include_dev_plugins": false,
      "use_dev_branches": false
    },
    "ci": {
      "include_dev_plugins": false,
      "use_dev_branches": false,
      "skip_optional": true
    }
  }
}
```

**⚠️ Important**: Replace the repository URLs with your actual plugin repositories!

#### 1.3 Create Plugin Manager Script
**File:** `plugin_manager.py` (in project root)

Copy the complete `plugin_manager.py` content from the artifacts above.

#### 1.4 Create Local Setup Helper
**File:** `setup_plugins.py` (in project root)

Copy the complete `setup_plugins.py` content from the artifacts above.

#### 1.5 Create GitHub Actions Workflow
**File:** `.github/workflows/build.yml`

Copy the complete GitHub Actions workflow from the artifacts above.

### Step 2: Test Local Setup

#### 2.1 Verify File Structure
Your project should look like this:
```
AetherOnePy/
├── .github/workflows/build.yml     ✅ NEW
├── plugins-config.json             ✅ NEW  
├── plugin_manager.py               ✅ NEW
├── setup_plugins.py                ✅ NEW
├── py/
│   ├── main.py                     ✅ EXISTING
│   ├── setup.py                    ✅ EXISTING
│   └── .venv/                      ✅ EXISTING
├── desktop_launcher.py             ✅ EXISTING
└── AetherOnePy.spec                ✅ EXISTING
```

#### 2.2 Test Plugin Manager
```bash
# Test plugin configuration
python plugin_manager.py --action list

# Expected output:
# 📋 Configured Plugins:
#   AetherOnePySocialPlugin:
#     Status: ✅ ENABLED | 🔓 OPTIONAL | 📂 NOT INSTALLED
```

#### 2.3 Run Complete Setup
```bash
# This installs everything automatically
python setup_plugins.py
```

**Expected output:**
```
🔧 Setting up AetherOnePy plugins for local development...
📦 Step 1: Installing base dependencies...
Using existing py/setup.py for base dependencies...
✅ Base dependencies installed!

🔌 Step 2: Downloading and installing plugins...
🚀 Starting plugin installation...
🔧 Installing plugin: AetherOne Social Plugin
  📥 Cloning https://github.com/isuretpolos/AetherOnePySocialPlugin.git
  ✅ Successfully cloned to py/plugins/AetherOnePySocialPlugin
  ✅ Plugin AetherOnePySocialPlugin installed successfully

📦 Step 3: Installing plugin dependencies...
✅ Plugin dependencies installed!

🎉 Plugin setup completed successfully!
```

#### 2.4 Verify Installation
```bash
# Check installed plugins
python plugin_manager.py --action list

# Check directories
dir py/plugins                    # Windows
ls py/plugins                     # Linux/Mac

# You should see your plugin directories
```

### Step 3: Test Your Flask App

```bash
# Start your Flask app with plugins
cd py
python main.py --port 7000

# Check if plugins loaded in the console output:
# Plugin 'AetherOnePySocialPlugin' routes loaded and registered...
# Plugin 'FinCompassPlugin' routes loaded and registered...
```

**Visit:** http://localhost:7000 - Your plugins should be working!

### Step 4: Commit and Push

```bash
# Add new files to git
git add .github/workflows/build.yml
git add plugins-config.json
git add plugin_manager.py  
git add setup_plugins.py
git add README-PLUGINS.md

# Commit
git commit -m "Add automatic plugin management system"

# Push
git push origin main
```

### Step 5: Verify GitHub Actions

1. Go to your repository on GitHub
2. Click **Actions** tab
3. You should see **"Build AetherOnePy Executable with Plugins"** workflow running
4. Wait for it to complete (~10-15 minutes)
5. Download the artifact: **"AetherOnePy-WithPlugins-ci-[commit]"**

---

## 🔧 Adding Your Own Plugins

### Method 1: Add to plugins-config.json

1. **Edit `plugins-config.json`**:
```json
{
  "plugins": {
    "YourNewPlugin": {
      "name": "Your Plugin Name",
      "description": "What your plugin does",
      "version": "1.0.0", 
      "author": "Your Name",
      "repository": {
        "type": "github",
        "url": "https://github.com/yourusername/YourPlugin.git",
        "branch": "main"
      },
      "enabled": true,
      "required": false,
      "dependencies": {
        "python": ["requests"],
        "system": []
      },
      "install_path": "py/plugins/YourNewPlugin"
    }
  }
}
```

2. **Run setup again**:
```bash
python setup_plugins.py
```

### Method 2: Manual Plugin Installation

```bash
# Clean existing plugins (optional)
python plugin_manager.py --action clean

# Install with new configuration
python plugin_manager.py --environment development --action install
```

---

## 🏗️ Plugin Development

### Create a New Plugin

1. **Create repository structure**:
```
YourPlugin/
├── plugin.json              # Plugin metadata
├── routes.py                 # Flask routes  
├── requirements.txt          # Dependencies
├── templates/                # HTML templates
├── static/                   # CSS/JS files
└── README.md                # Documentation
```

2. **Create `plugin.json`**:
```json
{
  "name": "Your Plugin Name",
  "version": "1.0.0",
  "description": "Brief description",
  "author": "Your Name", 
  "ui": "plugin.html",
  "category": "utility"
}
```

3. **Create `routes.py`**:
```python
from flask import Blueprint, render_template, jsonify

def create_blueprint():
    bp = Blueprint('your_plugin', __name__)
    
    @bp.route('/')
    def index():
        return render_template('plugin.html')
    
    @bp.route('/api/data')
    def get_data():
        return jsonify({"message": "Hello from plugin!"})
    
    return bp
```

4. **Create `requirements.txt`**:
```
requests>=2.25.0
flask>=2.0.0
```

5. **Test locally**: Your existing `py/setup.py` will automatically install the requirements!

---

## ❓ Troubleshooting

### Plugin Not Downloading
```bash
# Check configuration
python plugin_manager.py --action list

# Try manual installation
python plugin_manager.py --environment development --action install

# Check repository access
git clone https://github.com/yourusername/YourPlugin.git /tmp/test
```

### Plugin Not Loading in Flask
```bash
# Check if plugin directory exists
ls py/plugins/YourPlugin

# Check if routes.py has create_blueprint function
grep -n "create_blueprint" py/plugins/YourPlugin/routes.py

# Check Flask console output for import errors
cd py && python main.py --port 7000
```

### Dependencies Not Installing
```bash
# Check plugin requirements.txt
cat py/plugins/YourPlugin/requirements.txt

# Run setup.py manually
cd py && python setup.py

# Install specific package manually
pip install package-name
```

### GitHub Actions Failing
1. Check **Actions** tab in GitHub repository
2. Click on failed workflow to see logs
3. Look for error messages in "Install plugins" step
4. Common issues:
   - Invalid JSON in plugins-config.json
   - Repository not accessible
   - Missing dependencies

---

## 🎯 Quick Commands Reference

```bash
# Local development setup
python setup_plugins.py

# List configured plugins  
python plugin_manager.py --action list

# Install plugins only
python plugin_manager.py --environment development --action install

# Clean all plugins
python plugin_manager.py --action clean

# Test your Flask app
cd py && python main.py --port 7000

# Build executable locally
pyinstaller AetherOnePy.spec --noconfirm
```

---

## 🚀 What Happens Automatically

### Local Development (`python setup_plugins.py`)
1. ✅ Installs base dependencies via your `py/setup.py`
2. ✅ Downloads all enabled plugins from repositories  
3. ✅ Installs plugin requirements via your `py/setup.py`
4. ✅ Ready to run: `cd py && python main.py --port 7000`

### GitHub Actions (on push/PR/release)
1. ✅ Sets up Python environment
2. ✅ Installs base dependencies via your `py/setup.py` 
3. ✅ Downloads all plugins for CI environment
4. ✅ Installs plugin dependencies via your `py/setup.py`
5. ✅ Builds executable with PyInstaller
6. ✅ Creates downloadable artifact with all plugins included
7. ✅ Optionally creates GitHub release

### Your Existing Code
- ✅ **No changes needed** to `py/setup.py` or `py/main.py`
- ✅ **Works exactly as before** for local development
- ✅ **Plugin requirements automatically detected** via `install_plugin_requirements()`
- ✅ **Raspberry Pi detection still works**

---

## 💡 Pro Tips

1. **Test plugins individually**: Add one plugin at a time to plugins-config.json
2. **Use development environment**: Set `"enabled": false` for unstable plugins in production
3. **Version pinning**: Use specific branches/tags for stable builds
4. **Monitor builds**: Check GitHub Actions tab regularly for build failures
5. **Keep plugins updated**: Regularly update plugin versions in configuration

---

## 🆘 Need Help?

1. **Check this README** for common issues
2. **Look at GitHub Actions logs** for build errors
3. **Test locally first** before pushing to GitHub
4. **Check plugin repositories** for specific plugin issues
5. **Verify JSON syntax** in plugins-config.json

**Remember**: Your existing `py/setup.py` with `install_plugin_requirements()` function is the core of this system - it handles all dependency management automatically! 🎉