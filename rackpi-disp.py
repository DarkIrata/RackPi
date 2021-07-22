# RackPi - Display
# Author DarkIrata

# Imports
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import RPi.GPIO as GPIO
import busio
import adafruit_ssd1306
import psutil
import socket
import time
import shutil
import subprocess
import traceback

## Configuration ##
LedPin = 23                  # PI, GPIO Pin
ButtonPin = 20               # PI, GPIO Pin
DisplayTimeout = 10          # Seconds until displays turns off when no input is given
LongPressTime = 2            # Seconds until a hold is registered as long press
RotationFromPins = False     # True = From Pins to Right | False = Mirrored 
InvertButton = False         # Invert Button Input from GPIO Read


####### Don't change anything below this line #######

Version = "1.0.0"
SplashScreenTimeout = 1.25

## HELPER ###########################################
class Drawer:
    Canvas: Image = None
    Pen: ImageDraw = None
    Font: ImageFont = None
    width = 0
    height = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height

        print("Creating canvas for screen")
        # '1' for 1-bit color
        self.Canvas = Image.new("1", (width, height))

        print("Creating pen with default font")
        self.Pen = ImageDraw.Draw(self.Canvas)
        self.Font = ImageFont.load_default()

    def ClearCanvas(self):
        # Draw a black filled box to clear the image.
        self.Pen.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        
    def WriteOnCanvas(self, text: str, line = 0, xOffset = 0, yOffset = 0):
        lineOffset = line * 12
        y = yOffset + lineOffset - 2 # 2 => Top Padding
        self.Pen.text((xOffset, y), text, font=self.Font, fill=255)

def GetDataFromCommand(cmd: str):
    output = subprocess.check_output(cmd, shell = True)
    return output.decode('UTF-8')

## PAGES ###########################################
class Page:
    drawer: Drawer = None
    longPressHandled = False
    nextUpdate = 0

    def __init__(self, drawer: Drawer):
        self.drawer = drawer

    def EnterPage(self):
        self.nextUpdate = 0

    def LeavePage(self):
        self.longPressHandled = False

    def CanUpdate(self, timer):
        if self.nextUpdate > 0:
            self.nextUpdate -= 1
            return False
        else:
            self.nextUpdate = timer
            return True

    def UpdateCanvas(self):
        self.drawer.ClearCanvas()
        self.drawer.WriteOnCanvas("- NO PAGE DATA SET -" + Version, line=1, xOffset=15)

    def OnLongPress(self):
        self.longPressHandled = not self.longPressHandled
        self.nextUpdate = 0

class NetInfoPage(Page):
    def __init__(self, drawer: Drawer):
        Page.__init__(self, drawer)

    def UpdateCanvas(self):
        if not self.CanUpdate(10):
            return
            
        self.drawer.ClearCanvas()
        if not self.longPressHandled:
            self.DrawPage1()
        else:
            self.DrawPage2()

    def DrawPage1(self):
        hostname = socket.gethostname()
        ip = GetDataFromCommand("hostname -I | cut -d\' \' -f1")
        
        self.drawer.WriteOnCanvas("<-- NET INFO 1/2 -->", line=0, xOffset=2)
        self.drawer.WriteOnCanvas("HOST: " + hostname, line=1)
        self.drawer.WriteOnCanvas("IP  : " + ip, line=2)

    def DrawPage2(self):
        dns = GetDataFromCommand("grep -Pom 1 '^nameserver \K\S+' /etc/resolv.conf")

        self.drawer.WriteOnCanvas("<-- NET INFO 2/2 -->", line=0, xOffset=2)
        self.drawer.WriteOnCanvas("DNS : " + dns, line=1)

class HostInfoPage(Page):
    def __init__(self, drawer: Drawer):
        Page.__init__(self, drawer)

    def UpdateCanvas(self):
        if not self.CanUpdate(3):
            return

        self.drawer.ClearCanvas()
        if not self.longPressHandled:
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
        
        self.drawer.WriteOnCanvas("<-- HOST INFO 1/2 -->", line=0)
        self.drawer.WriteOnCanvas("CPU:" + cpuUsage + "%  TEMP:" + temp + "°C", line=1)
        self.drawer.WriteOnCanvas("MEM:" + memUsage + "%  DISK:" + usedPct + "%", line=2)

    def DrawPage2(self):
        load = GetDataFromCommand("cut -f 1-3 -d ' ' /proc/loadavg")

        self.drawer.WriteOnCanvas("<-- HOST INFO 2/2 -->", line=0)
        self.drawer.WriteOnCanvas("LOAD: " + load, line=1)

class RebootPage(Page):
    def __init__(self, drawer: Drawer):
        Page.__init__(self, drawer)

    def UpdateCanvas(self):
        if not self.CanUpdate(100):
            return
        
        self.drawer.ClearCanvas()
        self.drawer.WriteOnCanvas(".......Reboot.......", line=0)
        self.drawer.WriteOnCanvas("   Hold Button " + str(LongPressTime) + " sec", line=1)
        self.drawer.WriteOnCanvas("      To Reboot     ", line=2)

    def OnLongPress(self):
        self.drawer.ClearCanvas()
        cmd = "sudo reboot now"
        print("REBOOT")
        subprocess.Popen(cmd, shell = True)

class SplashScreenPage(Page):
    def __init__(self, drawer: Drawer):
        Page.__init__(self, drawer)

    def UpdateCanvas(self):
        self.drawer.ClearCanvas()
        self.drawer.WriteOnCanvas("RackPI v" + Version, 0, xOffset=18, yOffset=3)
        self.drawer.WriteOnCanvas("+-+-+-+-+-+-+-+-+-+-+", 1)
        self.drawer.WriteOnCanvas("github.com/DarkIrata", 2, yOffset=-5)

## MAIN ###########################################
class Program:
    pages = None
    currentIndex = -1
    display = None
    currentPage = None
    displayOnTime = None
    buttonPressTime = None
    loopSleepTime = 0.02   # 20ms
    screenWidth = 128
    screenHeight = 32
    drawer: Drawer = None

    def __init__(self):
        self.SetupHardware()
        self.SetupScreen()
        self.SetupPages()

        print("RackPI Script initialized!")
        GPIO.output(LedPin, GPIO.HIGH)
        try:
            self.Run()
        except Exception as e:
            self.drawer.ClearCanvas()
            self.UpdateScreen()
            if not e is KeyboardInterrupt:
                traceback.print_exc()
                try:
                    self.RunBlinki()
                except:
                    pass

    def SetupHardware(self):
        print("Initialize GPIO Pins")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LedPin, GPIO.OUT)
        GPIO.setup(ButtonPin, GPIO.IN)

        print("Initialize I2C Interface")
        i2c = busio.I2C(SCL, SDA)
        
        print("Initialize SSD1306 Display")
        self.display = adafruit_ssd1306.SSD1306_I2C(self.screenWidth, self.screenHeight, i2c)
        # Clear display.
        if RotationFromPins:
            self.display.rotation = 0
        else:
            self.display.rotation = 2
        self.display.fill(0)
        self.display.show()

    def SetupScreen(self):
        self.drawer = Drawer(self.screenWidth, self.screenHeight)
        self.ShowSplashScreen()
        self.ClearScreen()

    def SetupPages(self):
        print("Initialize pages")
        self.pages = [
            NetInfoPage(self.drawer),
            HostInfoPage(self.drawer),
            RebootPage(self.drawer),
        ]

    def ShowSplashScreen(self):
        self.ShowPage(SplashScreenPage(self.drawer), SplashScreenTimeout)
    
    def ClearScreen(self):
        self.drawer.ClearCanvas()
        self.UpdateScreen()
        self.displayOnTime = None
        self.currentPage = None

    def UpdateScreen(self):
        self.display.image(self.drawer.Canvas)
        self.display.show()

    def ShowPage(self, page: Page, freeze = 0):
        if self.currentPage != None:
            self.currentPage.LeavePage()

        self.currentPage = page

        if self.currentPage != None:
            self.currentPage.UpdateCanvas()
            self.currentPage.EnterPage()
        else:
            self.drawer.ClearCanvas()

        self.UpdateScreen()
        time.sleep(freeze)

    # Fallback to somewhat warn when script has an error
    def RunBlinki(self):
        state = False
        while True:
            if state:
                GPIO.output(LedPin, GPIO.HIGH)
            else:
                GPIO.output(LedPin, GPIO.LOW)
            
            state = not state
            time.sleep(0.35)

    def Run(self):
        btnResExpected = 0
        if InvertButton:
            btnResExpected = 1

        while True:
            btnPressed = GPIO.input(ButtonPin) == btnResExpected

            self.HandleButton(btnPressed)
            self.HandleScreenTimeout(btnPressed)

            time.sleep(self.loopSleepTime)

    def HandleButton(self, btnPressed):
        if btnPressed:
            if self.buttonPressTime == None:
                self.buttonPressTime = datetime.now()
        else:
            timeDif = 0
            if self.buttonPressTime != None:
                cur = datetime.now()
                timeDif = (cur - self.buttonPressTime).total_seconds()
                if timeDif == 0 and cur.microsecond > self.buttonPressTime.microsecond:
                    timeDif = -1 #Force Next Button

                self.buttonPressTime = None

            if timeDif >= LongPressTime - 1:
                self.HandleLongPress()
            elif timeDif != 0:
                self.HandleShortPress()

            self.UpdateScreenPage()

    def HandleScreenTimeout(self, btnPressed):
        if self.currentPage != None:
            if btnPressed:
                self.displayOnTime = None
            else:
                if self.displayOnTime == None:
                    self.displayOnTime = datetime.now()
                
                if self.displayOnTime != None and (datetime.now() - self.displayOnTime).total_seconds() >= DisplayTimeout - 1:
                    self.ShowPage(None)
                    self.displayOnTime = None
                    self.currentIndex = -1
    
    def HandleShortPress(self):
        self.currentIndex += 1
        if self.currentIndex >= len(self.pages):
            self.currentIndex = 0
        
        self.ShowPage(self.pages[self.currentIndex])

    def HandleLongPress(self):
        if self.currentPage != None:
            self.currentPage.OnLongPress()
        
    def UpdateScreenPage(self):
        if self.currentPage == None:
            return

        self.currentPage.UpdateCanvas()
        self.UpdateScreen()

# My code, my rules~
if __name__== "__main__":
  Program()
