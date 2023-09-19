# RackPi - Display
# Author DarkIrata

# Imports
from Utilities.Drawer import Drawer
from Utilities.Helper import *
from Pages.PageBase import PageBase
from board import SCL, SDA
from datetime import datetime
import RPi.GPIO as GPIO
import busio
import adafruit_ssd1306
import time
import traceback
import json
import os.path


## MAIN ###########################################
class Program:
    ## Configuration Fallback ##
    LedPin = 23                  # PI, GPIO Pin
    ButtonPin = 20               # PI, GPIO Pin
    DisplayTimeout = 7           # Seconds until displays turns off when no input is given
    LongPressTime = 2            # Seconds until a hold is registered as long press
    RotationFromPins = False     # True = From Pins to Right | False = Mirrored 
    ActivePages = ["NetInfo", "HostInfo", "Reboot", "SplashScreen"]
    SplashScreenTimeout = 1.25
    LoopSleepTime = 0.15   # 150ms

    ##### !! Dont change anything below this if you dont know what you are doing !! #####

    pages = []
    currentIndex = -1
    display = None
    currentPage = None
    displayOnTime = None
    buttonPressTime = None
    screenWidth = 128
    screenHeight = 32
    drawer: Drawer = None
    splashScreenPage = None
    config = None

    def __init__(self):
        self.LoadConfig()
        self.SetupHardware()
        self.SetupScreen()
        self.SetupPages()
        self.ShowSplashScreen()
        self.ClearScreen()

        print("RackPI Script initialized!")
        GPIO.output(self.LedPin, GPIO.HIGH)
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
        
    def LoadConfig(self):
        path = os.path.dirname(__file__) + '/Data/config.json'
        check_file = os.path.isfile(path)
        if not check_file:
            print("WARNING: Config not found. Falling back to defaults..")
            return

        print("Loading config..")
        with open(path, "r") as f:
            self.config = json.load(f)

        self.LedPin = self.config["LedPin"]
        self.ButtonPin = self.config["ButtonPin"]
        self.DisplayTimeout = self.config["DisplayTimeout"]
        self.LongPressTime = self.config["LongPressTime"]
        self.RotationFromPins = self.config["RotationFromPins"]
        self.ActivePages = self.config["ActivePages"]
        self.SplashScreenTimeout = self.config["SplashScreenTimeout"]
        self.LoopSleepTime = self.config["RunLoopSleepTime"]

        print("Config loaded!")

    def SetupHardware(self):
        print("Initialize GPIO Pins")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LedPin, GPIO.OUT)
        GPIO.setup(self.ButtonPin, GPIO.IN)

        print("Initialize I2C Interface")
        i2c = busio.I2C(SCL, SDA)
        
        print("Initialize SSD1306 Display")
        self.display = adafruit_ssd1306.SSD1306_I2C(self.screenWidth, self.screenHeight, i2c)
        # Clear display.
        if self.RotationFromPins:
            self.display.rotation = 0
        else:
            self.display.rotation = 2
        self.display.fill(0)
        self.display.show()

    def SetupScreen(self):
        self.drawer = Drawer(self.screenWidth, self.screenHeight)
        self.ClearScreen()

    def SetupPages(self):
        print("Initialize pages")
        baseModulePath = "Pages."
        try:
            self.splashScreenPage = CreatePageActivator(baseModulePath + "SplashScreen")(self.drawer, self.config)
        except:
            print("SplashScreen couldn't be created")

        for pageName in self.ActivePages:
            activator = CreatePageActivator(baseModulePath + pageName)
            if activator != None:
                print("Creating page instance for '" + pageName + "'")
                self.pages.append(activator(self.drawer, self.config))

    def ShowSplashScreen(self):
        if self.splashScreenPage != None:
            self.ShowPage(self.splashScreenPage, self.SplashScreenTimeout)

        self.splashScreenPage = None
    
    def ClearScreen(self):
        self.drawer.ClearCanvas()
        self.UpdateScreen()
        self.displayOnTime = None
        self.currentPage = None

    def UpdateScreen(self):
        self.display.image(self.drawer.Canvas)
        self.display.show()

    def ShowPage(self, page: PageBase, freeze = 0):
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
                GPIO.output(self.LedPin, GPIO.HIGH)
            else:
                GPIO.output(self.LedPin, GPIO.LOW)
            
            state = not state
            time.sleep(0.35)

    def Run(self):
        while True:
            self.HandleButton()
            self.UpdateScreenPage()
            self.HandleScreenTimeout()
            time.sleep(self.LoopSleepTime)
            
    def HandleButton(self):
        btnPressed = GPIO.input(self.ButtonPin) == 0

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

            if timeDif >= self.LongPressTime - 1:
                self.HandleLongPress()
            elif timeDif != 0:
                self.HandleShortPress()

    def HandleScreenTimeout(self):
        if self.currentPage != None:            
            if self.displayOnTime != None and (datetime.now() - self.displayOnTime).total_seconds() >= self.DisplayTimeout - 1:
                self.ShowPage(None)
                self.displayOnTime = None
                self.currentIndex = -1
    
    def HandleShortPress(self):
        self.HandlePress()
        self.currentIndex += 1
        if self.currentIndex >= len(self.pages):
            self.currentIndex = 0
        
        self.ShowPage(self.pages[self.currentIndex])

    def HandleLongPress(self):
        self.HandlePress()
        if self.currentPage != None:
            self.currentPage.OnLongPress()

    def HandlePress(self):
        self.displayOnTime = datetime.now()

        
    def UpdateScreenPage(self):
        if self.currentPage == None:
            return

        self.currentPage.UpdateCanvas()
        self.UpdateScreen()

# My code, my rules~
if __name__== "__main__":
  Program()
