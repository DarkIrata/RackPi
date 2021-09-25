from Data.Drawer import Drawer
from Data.Helper import *
from Pages.MultiPageBase import MultiPageBase
import socket

class NetInfo(MultiPageBase):
    def __init__(self, drawer: Drawer):
        MultiPageBase.__init__(self, 2, drawer)

    def UpdateCanvas(self):
        if not self.CanUpdate(10):
            return
            
        self.drawer.ClearCanvas()
        self.drawer.WriteOnCanvas("<-- NET INFO " + self.GetCurrentPageTitle() + " -->", line=0, xOffset=2)
        if self.CurrentPageIndex == 1:
            self.DrawPage1()
        else:
            self.DrawPage2()

    def DrawPage1(self):
        hostname = socket.gethostname()
        ip = GetDataFromCommand("hostname -I | cut -d\' \' -f1")
        
        self.drawer.WriteOnCanvas("HOST: " + hostname, line=1)
        self.drawer.WriteOnCanvas("IP  : " + ip, line=2)

    def DrawPage2(self):
        dns = GetDataFromCommand("grep -Pom 1 '^nameserver \K\S+' /etc/resolv.conf")

        self.drawer.WriteOnCanvas("DNS : " + dns, line=1)