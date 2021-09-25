from importlib import import_module
import subprocess
import traceback
import Pages.PageBase as PageBase

def GetDataFromCommand(cmd: str) -> str:
    output = subprocess.check_output(cmd, shell = True)
    return output.decode('UTF-8')

def CreatePageActivator(modulePath: str) -> PageBase:
    try:
        print("Creating activator for '" + modulePath + "'")
        className = modulePath.rsplit('.', 1)[1]
        module = import_module(modulePath)
        return getattr(module, className)

    except Exception as e:
        print("ERROR: Couldn't create activator for '" + modulePath + "'")
        traceback.print_exc()

        return None