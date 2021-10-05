from Data.Drawer import Drawer
from Data.Helper import *
from Pages.PageBase import PageBase

class MultiPageBase(PageBase):

    PageCount = 1
    CurrentPageIndex = 1

    def __init__(self, pageCount, drawer: Drawer):
        PageBase.__init__(self, drawer)
        self.PageCount = pageCount

    def OnLongPress(self):
        PageBase.OnLongPress(self)
        self.CurrentPageIndex += 1
        if self.CurrentPageIndex > self.PageCount:
            self.CurrentPageIndex = 1

    def LeavePage(self):
        PageBase.LeavePage(self)
        self.CurrentPageIndex = 1

    def GetCurrentPageTitle(self) -> str:
        return str(self.CurrentPageIndex) + "/" + str(self.PageCount)
