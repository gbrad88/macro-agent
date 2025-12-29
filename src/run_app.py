import sys
import os
import traceback
from datetime import datetime
import subprocess

# --- EMERGENCY LOGGING SETUP ---
log_file = os.path.join(os.environ.get("USERPROFILE", "."), "Desktop", "macro_agent_crash.log")

def log(msg):
    try:
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except:
        pass

def ensure_desktop_shortcut():
    """
    Creates a shortcut on the User's Desktop using VBScript to avoid 
    external dependencies like pywin32 or winshell.
    """
    try:
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        link_path = os.path.join(desktop, "Macro Agent.lnk")
        
        if os.path.exists(link_path):
            log("Shortcut already exists.")
            return

        log(f"Creating shortcut at: {link_path}")
        
        # Target is the executable itself
        target = os.path.abspath(sys.executable)
        working_dir = os.path.dirname(target)
        
        # VBScript to create shortcut
        vbs_script = f"""
            Set oWS = WScript.CreateObject("WScript.Shell")
            sLinkFile = "{link_path}"
            Set oLink = oWS.CreateShortcut(sLinkFile)
            oLink.TargetPath = "{target}"
            oLink.WorkingDirectory = "{working_dir}"
            oLink.Description = "Antigravity Macro Agent"
            oLink.Save
        """
        
        vbs_path = os.path.join(working_dir, "create_shortcut.vbs")
        with open(vbs_path, "w") as f:
            f.write(vbs_script)
            
        subprocess.run(["cscript", "//Nologo", vbs_path], check=True)
        os.remove(vbs_path)
        log("Shortcut created successfully.")
        
    except Exception as e:
        log(f"Failed to create shortcut: {e}")

try:
    log("========================================")
    log("Initializing MacroAgent (v1.13)...")
    log(f"Executable: {sys.executable}")
    
    # Kill environment variables that might leak User/System site packages
    os.environ.pop("PYTHONPATH", None)
    os.environ.pop("PYTHONHOME", None)
    os.environ["PYTHONNOUSERSITE"] = "1"
    
    # --- CRITICAL: ISOLATE ENVIRONMENT BEFORE IMPORTING STREAMLIT ---
    if getattr(sys, 'frozen', False):
        log("Running in Frozen (MSI) mode.")
        ensure_desktop_shortcut()
        
        app_root = os.path.dirname(os.path.abspath(sys.executable))
        log(f"App Root: {app_root}")
        
        # RUTHLESS BLACKLIST: Remove any path that looks like it belongs to the user or system python
        # We cannot trust Whitelisting because of casing/symlink issues.
        original_path = sys.path.copy()
        log(f"Original sys.path: {original_path}")
        
        clean_path = []
        for p in original_path:
            p_lower = p.lower()
            if "appdata" in p_lower or "roaming" in p_lower or "python3" in p_lower or "site-packages" in p_lower:
                # Exception: If the path is actually INSIDE our app root (e.g. bundled site-packages), keep it
                if app_root.lower() in p_lower:
                    clean_path.append(p)
                else:
                    log(f"Dropping toxic path: {p}")
            else:
                clean_path.append(p)
        
        # Ensure critical bundle paths exist at the VERY FRONT
        lib_path = os.path.join(app_root, "lib")
        zip_path = os.path.join(app_root, "library.zip")
        
        # Prepend in reverse order of priority (last prepend = first in list)
        if app_root not in clean_path: clean_path.insert(0, app_root)
        if zip_path not in clean_path: clean_path.insert(0, zip_path)
        if lib_path not in clean_path: clean_path.insert(0, lib_path)
        
        sys.path = clean_path
        log(f"RUTHLESS CLEAN sys.path: {sys.path}")
        
        # Compatibility alias for downstream code
        base_dir = app_root
    else:
        log("Running in Dev (Script) mode.")
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Now it is safe to import application dependencies
    log("Importing streamlit...")
    import streamlit.web.cli as stcli
    log("Streamlit imported successfully.")
    
    def resolve_path(path):
        if getattr(sys, "frozen", False):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)
        return os.path.join(basedir, path)

    if __name__ == "__main__":
        dashboard_path = os.path.join(base_dir, "src", "dashboard.py")
        
        # Check if we moved it to root or kept in src
        if not os.path.exists(dashboard_path):
            dashboard_path = os.path.join(base_dir, "dashboard.py")
            
        log(f"Launching dashboard from: {dashboard_path}")
        
        if not os.path.exists(dashboard_path):
             raise FileNotFoundError(f"Dashboard script not found at {dashboard_path}")

        # Simulate "streamlit run dashboard.py"
        sys.argv = [
            "streamlit",
            "run",
            dashboard_path,
            "--global.developmentMode=false",
        ]
        log("Invoking Streamlit CLI...")
        sys.exit(stcli.main())

except Exception:
    error_msg = traceback.format_exc()
    log("CRITICAL ERROR CAUGHT:")
    log(error_msg)
    print("AN ERROR OCCURRED. SEE 'macro_agent_crash.log' ON YOUR DESKTOP.")
    print(error_msg)
    input("Press Enter to close window...")
    sys.exit(1)
