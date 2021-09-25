from Data.Drawer import Drawer
from Data.Helper import *
from Pages.PageBase import PageBase

class Reboot(PageBase):
    def __init__(self, drawer: Drawer):
        PageBase.__init__(self, drawer)

    def UpdateCanvas(self):
        if not self.CanUpdate(100):
            return
        
        self.drawer.ClearCanvas()
        self.drawer.WriteOnCanvas(".......Reboot.......", line=0)
        self.drawer.WriteOnCanvas("    Hold Button     ", line=1)
        self.drawer.WriteOnCanvas("     To Reboot     ", line=2)

    def OnLongPress(self):
        self.drawer.ClearCanvas()
        cmd = "sudo reboot now"
        print("REBOOT")
        subprocess.Popen(cmd, shell = True)