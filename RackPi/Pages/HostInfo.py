from Data.Drawer import Drawer
from Data.Helper import *
from Pages.MultiPageBase import MultiPageBase
import psutil
import shutil

class HostInfo(MultiPageBase):
    def __init__(self, drawer: Drawer):
        MultiPageBase.__init__(self, 2, drawer)

    def UpdateCanvas(self):
        if not self.CanUpdate(3):
            return

        self.drawer.ClearCanvas()
        self.drawer.WriteOnCanvas("<-- HOST INFO " + self.GetCurrentPageTitle() + " -->", line=0)
        if self.CurrentPageIndex == 1:
            self.DrawPage1()
        else:
            self.DrawPage2()

    def DrawPage1(self):
        cpuUsage = "{:3.0f}".format(psutil.cpu_percent())
        memUsage = "{:3.0f}".format(psutil.virtual_memory().percent)

        rawTemp = float(GetDataFromCommand("cat /sys/class/thermal/thermal_zone0/temp"))
        temp = "{:3.1f}".format(round((rawTemp / 1000), 1))
        
        total, used, free = shutil.disk_usage("/")
        usedPct = "{:3.0f}".format(round((used / total) * 100, 1))
        
        self.drawer.WriteOnCanvas("CPU:" + cpuUsage + "%  TEMP:" + temp + "°C", line=1)
        self.drawer.WriteOnCanvas("MEM:" + memUsage + "%  DISK:" + usedPct + "%", line=2)

    def DrawPage2(self):
        load = GetDataFromCommand("cut -f 1-3 -d ' ' /proc/loadavg")
        uptime = GetDataFromCommand("uptime | awk -F'( |,|:)+' '{print $6,$7}'")

        self.drawer.WriteOnCanvas("LOAD: " + load, line=1)
        self.drawer.WriteOnCanvas("UPTIME: " + uptime, line=2)