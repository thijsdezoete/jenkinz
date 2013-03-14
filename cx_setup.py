import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "Jenkinz",
        version = "0.1",
        description = "Jenkinz tray application by Thijs de Zoete",
        options = {"build_exe" : {"includes" : "atexit" }},
        executables = [Executable("jenkins.py", base = base)])
