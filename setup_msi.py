import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sys", "streamlit", "altair", "pandas", "yfinance", "httpx", "dotenv", "typing"],
    "excludes": [],
    "include_files": [
        ("src", "src"), # Process the whole src folder to build root
        (".env", ".env")
    ]
}

# Base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Console" # Keep console for now to see errors, change to "Win32GUI" to hide

# MSI Options to create a Shortcut
bdist_msi_options = {
    "add_to_path": False,
    "initial_target_dir": r"[LocalAppDataFolder]\Programs\MacroAgent",
    "upgrade_code": "{8c5bc54f-c22b-4afd-8045-752cf150eb32}",
}

setup(
    name = "MacroAgent",
    version = "1.13",
    description = "Antigravity Macro Watchdog Agent",
    options = {
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables = [
        Executable(
            "src/run_app.py", 
            base=base, 
            target_name="MacroAgent.exe",
            # shortcut_name="Macro Agent", <--- HANDLED BY APP NOW
            # shortcut_dir="DesktopFolder", 
            icon=None
        )
    ]
)
