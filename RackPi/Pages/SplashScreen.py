from Utilities.Drawer import Drawer
from Utilities.Helper import *
from Pages.MultiPageBase import MultiPageBase

class SplashScreen(MultiPageBase):

    pos = -10

    def __init__(self, drawer: Drawer, config):
        MultiPageBase.__init__(self, 2, drawer, config)

    def UpdateCanvas(self):
        if not self.CanUpdate(0.15):
            return

        self.drawer.ClearCanvas()
        if self.CurrentPageIndex == 1:
            self.DrawPage1()
        else:
            self.DrawPage2()
        
    def DrawPage1(self):
        self.drawer.WriteOnCanvas("RackPI v1.1.0", 0, xOffset=16, yOffset=3)
        self.drawer.WriteOnCanvas("+-+-+-+-+-+-+-+-+-+-+", 1)
        self.drawer.WriteOnCanvas("github.com/DarkIrata", 2, yOffset=-5)

    def DrawPage2(self):
        self.pos += 15
        if self.pos > 128:
            self.pos = -10
        self.drawer.WriteOnCanvas("RackPI v1.1.0", 0, xOffset=16, yOffset=3)
        self.drawer.WriteOnCanvas("Eggo", 1, xOffset=self.pos)
        self.drawer.WriteOnCanvas("\(`o´)/", 2, xOffset=20, yOffset=-2)
