#!/usr/bin/env python3
"""
AetherOnePy Plugin Manager
Automatically downloads, installs, and manages plugins from various sources
"""

import json
import os
import sys
import subprocess
import shutil
import urllib.request
import urllib.error
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

# Windows compatibility for Unicode output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


class PluginManager:
    def __init__(self, config_file: str = "plugins-config.json", environment: str = "production"):
        self.config_file = config_file
        self.environment = environment
        self.config = self.load_config()
        self.project_root = Path.cwd()
        
    def load_config(self) -> Dict:
        """Load plugin configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {self.config_file} not found")
            return {"plugins": {}, "config": {}, "environments": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            return {"plugins": {}, "config": {}, "environments": {}}
    
    def get_environment_config(self) -> Dict:
        """Get configuration for current environment"""
        return self.config.get("environments", {}).get(self.environment, {})
    
    def should_install_plugin(self, plugin_config: Dict) -> bool:
        """Determine if a plugin should be installed based on environment and settings"""
        env_config = self.get_environment_config()
        
        # Skip disabled plugins
        if not plugin_config.get("enabled", True):
            return False
        
        # Skip optional plugins in CI environment
        if env_config.get("skip_optional", False) and not plugin_config.get("required", False):
            return False
        
        # Skip dev plugins in production
        if not env_config.get("include_dev_plugins", True) and plugin_config.get("dev_only", False):
            return False
        
        return True
    
    def get_branch_for_plugin(self, plugin_config: Dict) -> str:
        """Get the appropriate branch for a plugin based on environment"""
        env_config = self.get_environment_config()
        
        if env_config.get("use_dev_branches", False) and "dev_branch" in plugin_config.get("repository", {}):
            return plugin_config["repository"]["dev_branch"]
        
        return plugin_config.get("repository", {}).get("branch", "main")
    
    def clone_repository(self, repo_url: str, branch: str, target_path: str) -> bool:
        """Clone a Git repository to target path"""
        try:
            print(f"  [DOWNLOAD] Cloning {repo_url} (branch: {branch})")
            
            # Ensure target directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Remove existing directory if it exists
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            # Clone with specific branch
            cmd = [
                "git", "clone", 
                "--branch", branch,
                "--depth", "1",  # Shallow clone for faster downloads
                repo_url, 
                target_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"  [SUCCESS] Successfully cloned to {target_path}")
                
                # Remove .git directory to save space (optional)
                git_dir = os.path.join(target_path, ".git")
                if os.path.exists(git_dir):
                    shutil.rmtree(git_dir)
                    print(f"  [CLEANUP] Cleaned up .git directory")
                
                return True
            else:
                print(f"  [ERROR] Git clone failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Clone timed out for {repo_url}")
            return False
        except Exception as e:
            print(f"  [ERROR] Clone error: {e}")
            return False
    
    def download_archive(self, repo_url: str, branch: str, target_path: str) -> bool:
        """Download repository as ZIP archive (fallback method)"""
        try:
            print(f"  📦 Downloading archive from {repo_url}")
            
            # Convert GitHub URL to archive URL
            if "github.com" in repo_url:
                #archive_url = repo_url.replace(".git", "").replace("github.com", "github.com") + f"/archive/refs/heads/{branch}.zip"
                archive_url = repo_url.replace(".git", "") + f"/archive/refs/heads/{branch}.zip"
            else:
                print(f"  ❌ Archive download not supported for {repo_url}")
                return False
            
            # Download to temporary file
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
                urllib.request.urlretrieve(archive_url, tmp_file.name)
                
                # Extract archive
                import zipfile
                with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                    # Create target directory
                    os.makedirs(target_path, exist_ok=True)
                    
                    # Extract all files
                    for member in zip_ref.namelist():
                        # Skip the root directory in the archive
                        if "/" in member:
                            target_file = os.path.join(target_path, "/".join(member.split("/")[1:]))
                            if member.endswith("/"):
                                os.makedirs(target_file, exist_ok=True)
                            else:
                                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                                with zip_ref.open(member) as source, open(target_file, "wb") as target:
                                    target.write(source.read())
                
                # Cleanup
                os.unlink(tmp_file.name)
                
            print(f"  ✅ Successfully downloaded and extracted to {target_path}")
            return True
            
        except Exception as e:
            print(f"  ❌ Archive download error: {e}")
            return False
    
    def install_plugin_dependencies(self, plugin_config: Dict) -> bool:
        """Install Python dependencies for a plugin"""
        dependencies = plugin_config.get("dependencies", {})
        python_deps = dependencies.get("python", [])
        
        if not python_deps:
            return True
        
        try:
            print(f"  📦 Installing Python dependencies: {', '.join(python_deps)}")
            
            cmd = [sys.executable, "-m", "pip", "install"] + python_deps
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"  ✅ Dependencies installed successfully")
                return True
            else:
                print(f"  ⚠️ Some dependencies failed to install: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Dependency installation error: {e}")
            return False
    
    def run_setup_py_for_plugins(self) -> bool:
        """Run the existing setup.py to install plugin requirements"""
        setup_py_path = os.path.join(self.project_root, "py", "setup.py")
        
        if not os.path.exists(setup_py_path):
            print("  ⚠️ py/setup.py not found, skipping automatic plugin dependency installation")
            return True
        
        try:
            print("  🔄 Running py/setup.py to install plugin requirements...")
            
            # Change to py directory and run setup.py
            original_cwd = os.getcwd()
            os.chdir(os.path.join(self.project_root, "py"))
            
            result = subprocess.run([sys.executable, "setup.py"], 
                                  capture_output=True, text=True, timeout=300)
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                print("  ✅ Plugin requirements installed via setup.py")
                return True
            else:
                print(f"  ⚠️ setup.py execution had issues: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error running setup.py: {e}")
            try:
                os.chdir(original_cwd)
            except:
                pass
            return False
    
    def install_plugin(self, plugin_name: str, plugin_config: Dict) -> bool:
        """Install a single plugin"""
        print(f"\n[PLUGIN] Installing plugin: {plugin_config.get('name', plugin_name)}")
        
        if not self.should_install_plugin(plugin_config):
            print(f"  [SKIP] Skipping {plugin_name} (disabled or not required for {self.environment})")
            return True
        
        # Get repository info
        repo_info = plugin_config.get("repository", {})
        if not repo_info:
            print(f"  [ERROR] No repository information for {plugin_name}")
            return False
        
        repo_url = repo_info.get("url")
        branch = self.get_branch_for_plugin(plugin_config)
        install_path = plugin_config.get("install_path")
        
        if not all([repo_url, install_path]):
            print(f"  [ERROR] Missing required info: url={repo_url}, path={install_path}")
            return False
        
        # Convert to absolute path
        target_path = os.path.join(self.project_root, install_path)
        
        # Try to clone, fallback to archive download
        success = False
        if shutil.which("git"):
            success = self.clone_repository(repo_url, branch, target_path)
        
        if not success:
            print(f"  [FALLBACK] Git clone failed, trying archive download...")
            success = self.download_archive(repo_url, branch, target_path)
        
        if not success:
            print(f"  [ERROR] Failed to download {plugin_name}")
            return False
        
        # Install dependencies
        self.install_plugin_dependencies(plugin_config)
        
        # Verify installation
        if os.path.exists(target_path):
            print(f"  [SUCCESS] Plugin {plugin_name} installed successfully")
            return True
        else:
            print(f"  [ERROR] Plugin installation verification failed")
            return False
    
    def install_all_plugins(self) -> Tuple[int, int]:
        """Install all configured plugins"""
        print("[INSTALL] Starting plugin installation...")
        
        plugins = self.config.get("plugins", {})
        if not plugins:
            print("[INFO] No plugins configured")
            return 0, 0
        
        installed = 0
        failed = 0
        
        for plugin_name, plugin_config in plugins.items():
            try:
                if self.install_plugin(plugin_name, plugin_config):
                    installed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"[ERROR] Unexpected error installing {plugin_name}: {e}")
                failed += 1
        
        # After all plugins are installed, run setup.py to install their requirements
        if installed > 0:
            print(f"\n[DEPENDENCIES] Installing plugin dependencies...")
            self.run_setup_py_for_plugins()
        
        print(f"\n[SUMMARY] Installation Summary:")
        print(f"  [SUCCESS] Installed: {installed}")
        print(f"  [FAILED] Failed: {failed}")
        print(f"  [TOTAL] Total: {len(plugins)}")
        
        return installed, failed
    
    def list_plugins(self) -> None:
        """List all configured plugins with their status"""
        print("[PLUGINS] Configured Plugins:")
        
        plugins = self.config.get("plugins", {})
        if not plugins:
            print("  No plugins configured")
            return
        
        for plugin_name, plugin_config in plugins.items():
            status = "[ENABLED]" if plugin_config.get("enabled", True) else "[DISABLED]"
            required = "[REQUIRED]" if plugin_config.get("required", False) else "[OPTIONAL]"
            
            install_path = plugin_config.get("install_path", "")
            installed = "[INSTALLED]" if os.path.exists(install_path) else "[NOT INSTALLED]"
            
            print(f"  {plugin_name}:")
            print(f"    Name: {plugin_config.get('name', 'N/A')}")
            print(f"    Status: {status} | {required} | {installed}")
            print(f"    Version: {plugin_config.get('version', 'N/A')}")
            print(f"    Repository: {plugin_config.get('repository', {}).get('url', 'N/A')}")
            print()
    
    def clean_plugins(self) -> None:
        """Remove all installed plugins"""
        print("[CLEANUP] Cleaning installed plugins...")
        
        plugins = self.config.get("plugins", {})
        removed = 0
        
        for plugin_name, plugin_config in plugins.items():
            install_path = plugin_config.get("install_path")
            if install_path and os.path.exists(install_path):
                try:
                    shutil.rmtree(install_path)
                    print(f"  [REMOVED] {plugin_name}")
                    removed += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to remove {plugin_name}: {e}")
        
        print(f"[CLEANUP] Cleaned {removed} plugins")


def main():
    parser = argparse.ArgumentParser(description="AetherOnePy Plugin Manager")
    parser.add_argument("--config", default="plugins-config.json", help="Plugin configuration file")
    parser.add_argument("--environment", default="production", choices=["development", "production", "ci"], 
                       help="Environment mode")
    parser.add_argument("--action", choices=["install", "list", "clean"], default="install",
                       help="Action to perform")
    
    args = parser.parse_args()
    
    manager = PluginManager(args.config, args.environment)
    
    if args.action == "install":
        installed, failed = manager.install_all_plugins()
        sys.exit(0 if failed == 0 else 1)
    elif args.action == "list":
        manager.list_plugins()
    elif args.action == "clean":
        manager.clean_plugins()


if __name__ == "__main__":
    main()