from PIL import Image, ImageDraw, ImageFont

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