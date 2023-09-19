from Utilities.Drawer import Drawer
from Utilities.Helper import *
from Pages.PageBase import PageBase
import os

class Reboot(PageBase):
    inDocker = False
    
    def __init__(self, drawer: Drawer, config):
        PageBase.__init__(self, drawer, config)
        self.inDocker = os.environ.get('InsideDocker', False)

    def UpdateCanvas(self):
        if not self.CanUpdate(100):
            return
        
        self.drawer.ClearCanvas()
        if self.inDocker:
            self.drawer.WriteOnCanvas(".......Reboot.......", line=0)
            self.drawer.WriteOnCanvas("   not available    ", line=1)
            self.drawer.WriteOnCanvas("   inside docker    ", line=2)
        else:
            self.drawer.WriteOnCanvas(".......Reboot.......", line=0)
            self.drawer.WriteOnCanvas("    Hold Button     ", line=1)
            self.drawer.WriteOnCanvas("     To Reboot     ", line=2)

    def OnLongPress(self):
        self.drawer.ClearCanvas()
        cmd = "sudo reboot now"
        print("REBOOT")
        subprocess.Popen(cmd, shell = True)
