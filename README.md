# RackPi
Scripts for RackPI (https://www.thingiverse.com/thing:3022136)

Pages can be added and removed in the *RackPi.py*
The order in *ActivePages* is also used for displaying the pages. Names have to be same was files in /Pages

Support for Short and Long Press actions

Currently Available 
* NetInfo  (Hostname, IP Address, DNS Server)
* HostInfo (CPU %, MEM %, DISK %, TEMP °C, LOAD, UPTIME)
* Reboot   (Reboot on Longpress)
* SplashScreen

Pages can either inherit from *PageBase* or *MultiPageBase*
### PageBase:
Available Methods:
```python
    def EnterPage(self):            # Called on entering the page
        pass
    def LeavePage(self):            # Called on leaving the page
        pass
    def UpdateCanvas(self):         # Called on every update tick
        if not self.CanUpdate({UPDATE_AFTER_TICKLS}):     # To reduce cpu usage, check by CanUpdate with given Ticks amount
            return
        pass
    def OnLongPress(self):          # Called when button is long pressed
        pass
```
Perfectly for text display with Trigger Actions. Example Rebooting the device

### MultiPageBase(PageBase):
Available Methods:
```python
    def EnterPage(self):            # Called on entering the page (Main Page, not sub-pages)
        pass
    def LeavePage(self):            # Called on leaving the page (Main Page, not sub-pages)
        pass
    def UpdateCanvas(self):         # Called on every update tick
        if not self.CanUpdate({UPDATE_AFTER_TICKLS}):     # To reduce cpu usage, check by CanUpdate with given Ticks amount
            return
        pass
```
Perfectly for displaying multiple informations and split them into sub-pages.
Longpress is used to change to the next sub-page

- - -
Don't forget to add to rc.local

- - -
## Docker
`docker run -i -d --device /dev/i2c-1 --device /dev/gpiomem --net=host ghcr.io/darkirata/rackpi:main`

*Home Assistant tutorial for enabling I2C on Home Assistant OS - 05.10.2021*

https://www.home-assistant.io/common-tasks/os#enable-i2c

