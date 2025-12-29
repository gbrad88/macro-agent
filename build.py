import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('build'): shutil.rmtree('build')
if os.path.exists('dist'): shutil.rmtree('dist')

# Run PyInstaller
PyInstaller.__main__.run([
    'src/run_app.py',
    '--name=MacroAgent',
    '--onefile',
    '--clean',
    # Streamlit Hooks
    '--collect-all=streamlit',
    '--collect-all=altair',
    '--collect-all=pandas',
    '--hidden-import=streamlit',
    '--hidden-import=altair',
    # Data Files
    '--add-data=src/dashboard.py;src',  # Include dashboard source
    '--add-data=.env;.env' if os.path.exists('.env') else '', # Attempt to bundle env (optional)
])

print("Build Complete! Executable is in dist/MacroAgent.exe")
