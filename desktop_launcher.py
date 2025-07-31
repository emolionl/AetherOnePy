import subprocess
import time
import sys
import os
import webview
from screeninfo import get_monitors
import shutil

DEBUG = True

def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")
        sys.stdout.flush()

def find_python_executable():
    """Find a working Python executable"""
    debug_print("Finding Python executable...")
    
    if getattr(sys, 'frozen', False):
        # In PyInstaller, look for system Python
        candidates = ['python', 'py', 'python3']
        
        for candidate in candidates:
            found = shutil.which(candidate)
            if found:
                debug_print(f"Found Python: {found}")
                return found
        
        debug_print("No system Python found, trying common paths...")
        common_paths = [
            r'C:\Python311\python.exe',
            r'C:\Python310\python.exe',
            r'C:\Python39\python.exe',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                debug_print(f"Found Python at: {path}")
                return path
                
        debug_print("ERROR: No Python executable found!")
        return None
    else:
        # Development mode
        return sys.executable

def get_resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def on_window_closed():
    debug_print("Webview closed. Cleaning up...")
    if flask_process:
        debug_print("Terminating Flask process...")
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)
        except:
            flask_process.kill()
        debug_print("✓ Flask process terminated.")

def main():
    debug_print("=== AETHER ONE PY SUBPROCESS LAUNCHER ===")
    global flask_process
    flask_process = None
    flask_process = None

    os.makedirs('data', exist_ok=True)
    
    try:
        # Find Python
        python_exe = find_python_executable()
        if not python_exe:
            debug_print("Cannot find Python executable!")
            input("Press Enter to exit...")
            return
        
        # Get Flask script
        flask_script = get_resource_path('py/main.py')
        debug_print(f"Flask script: {flask_script}")
        
        if not os.path.exists(flask_script):
            debug_print(f"Flask script not found: {flask_script}")
            input("Press Enter to exit...")
            return
        
        # Start Flask process
        debug_print("Starting Flask process...")
        py_dir = get_resource_path('py')
        
        flask_process = subprocess.Popen([
            python_exe, 
            'main.py',  # Run from py directory
            '--port', '7000'
        ], 
        cwd=py_dir,  # Run from py directory
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        debug_print(f"Flask started with PID: {flask_process.pid}")
        
        # Wait for Flask to start
        debug_print("Waiting for Flask to start...")
        time.sleep(8)  # Give it more time
        
        # Check if Flask is still running
        if flask_process.poll() is not None:
            debug_print("Flask process died!")
            input("Press Enter to exit...")
            return
        
        # Test connection
        debug_print("Testing Flask connection...")
        import urllib.request
        
        for attempt in range(10):
            try:
                response = urllib.request.urlopen('http://localhost:7000', timeout=5)
                debug_print(f"✓ Flask responding! Status: {response.code}")
                break
            except Exception as e:
                debug_print(f"Attempt {attempt + 1}: {e}")
                time.sleep(2)
        else:
            debug_print("Could not connect to Flask!")
            input("Press Enter to exit...")
            return
        
        # Start webview
        debug_print("Starting webview...")
        monitor = get_monitors()[0]
        width, height = monitor.width, monitor.height
        
        class Api:
            def refresh_page(self):
                webview.windows[0].evaluate_js('window.location.reload()')
            def go_back(self):
                webview.windows[0].evaluate_js('window.history.back()')
            def go_forward(self):
                webview.windows[0].evaluate_js('window.history.forward()')

        # In your desktop_launcher.py, update the setup_bottom_bar function:

        def setup_bottom_bar():
            """Setup bottom bar that persists through page refreshes"""
            time.sleep(3)
            
            def inject_bar():
                try:
                    webview.windows[0].evaluate_js("""
                        // Remove existing elements if they exist
                        document.getElementById('control-bar')?.remove();
                        document.getElementById('control-trigger')?.remove();

                        // Create the floating trigger button
                        const trigger = document.createElement('div');
                        trigger.id = 'control-trigger';
                        trigger.style.cssText = `
                            position: fixed; bottom: 20px; left: 20px;
                            width: 50px; height: 50px; border-radius: 50%;
                            background: #764ba2;
                            display: flex; align-items: center; justify-content: center;
                            color: white; font-size: 24px; font-weight: bold;
                            cursor: pointer; z-index: 10001;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                            transition: background 0.3s;
                        `;
                        trigger.innerHTML = '≡';
                        document.body.appendChild(trigger);

                        // Create the hidden bottom bar
                        const controlBar = document.createElement('div');
                        controlBar.id = 'control-bar';
                        controlBar.style.cssText = `
                            position: fixed; bottom: 0; left: 0; right: 0; height: 60px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            display: flex; align-items: center; justify-content: center; gap: 20px;
                            box-shadow: 0 -2px 4px rgba(0,0,0,0.1); z-index: 10000;
                            opacity: 0; pointer-events: none; transition: opacity 0.3s;
                        `;

                        // Hover logic
                        let hoverTimeout;
                        const showBar = () => {
                            clearTimeout(hoverTimeout);
                            controlBar.style.opacity = '1';
                            controlBar.style.pointerEvents = 'auto';
                        };
                        const hideBar = () => {
                            hoverTimeout = setTimeout(() => {
                                controlBar.style.opacity = '0';
                                controlBar.style.pointerEvents = 'none';
                            }, 300);
                        };

                        trigger.addEventListener('mouseenter', showBar);
                        trigger.addEventListener('mouseleave', hideBar);
                        controlBar.addEventListener('mouseenter', showBar);
                        controlBar.addEventListener('mouseleave', hideBar);

                        const buttons = [
                            { text: '← Back', action: 'pywebview.api.go_back()' },
                            { text: '🔄 Refresh', action: 'pywebview.api.refresh_page()' },
                            { text: 'Forward →', action: 'pywebview.api.go_forward()' }
                        ];

                        buttons.forEach(btn => {
                            const button = document.createElement('button');
                            button.innerHTML = btn.text;
                            button.onclick = () => eval(btn.action);
                            button.style.cssText = `
                                background: rgba(255,255,255,0.2); color: white;
                                border: 1px solid rgba(255,255,255,0.3);
                                padding: 12px 20px; border-radius: 25px; cursor: pointer;
                                font-size: 14px; font-weight: 500; transition: all 0.2s;
                            `;
                            button.onmouseover = () => {
                                button.style.background = 'rgba(255,255,255,0.3)';
                                button.style.transform = 'translateY(-2px)';
                            };
                            button.onmouseout = () => {
                                button.style.background = 'rgba(255,255,255,0.2)';
                                button.style.transform = 'translateY(0)';
                            };
                            controlBar.appendChild(button);
                        });

                        document.body.appendChild(controlBar);

                        // Optional: mutation observer to reinject if removed
                        const observer = new MutationObserver(function() {
                            if (!document.getElementById('control-bar') || !document.getElementById('control-trigger')) {
                                setTimeout(() => {
                                    if (window.pywebview && window.pywebview.api) {
                                        window.pywebview.api.refresh_bottom_bar();
                                    }
                                }, 1000);
                            }
                        });

                        observer.observe(document.body, {
                            childList: true,
                            subtree: true
                        });

                        console.log('Floating trigger + hidden bottom bar injected');
                    """)
                    debug_print("✓ Bottom bar with trigger injected")
                except Exception as e:
                    debug_print(f"Bottom bar error: {e}")

            
            # Initial injection
            inject_bar()
            
            # Set up periodic re-injection
            def periodic_check():
                while True:
                    time.sleep(5)  # Check every 5 seconds
                    try:
                        # Check if the bar still exists
                        result = webview.windows[0].evaluate_js("document.getElementById('control-bar') !== null")
                        if not result:
                            debug_print("Bottom bar missing, re-injecting...")
                            inject_bar()
                    except:
                        break  # Window might be closed
            
            import threading
            threading.Thread(target=periodic_check, daemon=True).start()

        api = Api()
        
        window = webview.create_window(
            'AetherOnePy',
            'http://localhost:7000/',
            width=width,
            height=height,
            resizable=True,
            js_api=api
        )
        
        import threading
        threading.Thread(target=setup_bottom_bar, daemon=True).start()
        window.events.closed += on_window_closed
        webview.start()
        
    except KeyboardInterrupt:
        debug_print("Interrupted by user")
    except Exception as e:
        debug_print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
    finally:
        if flask_process:
            debug_print("Terminating Flask...")
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
            except:
                flask_process.kill()

if __name__ == "__main__":
    main()