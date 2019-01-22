import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class Display(object):

    WIDTH = 128
    HEIGHT = 64

    def __init__(self, reset_pin, dc_pin, spi_port, spi_device):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=reset_pin, dc=dc_pin,
                                                    spi=SPI.SpiDev(spi_port, spi_device, max_speed_hz=8000000))

        self.disp.begin()
        self.disp.clear()
        self.disp.display()

    def update(self, visible, infrared, temp, pressure, humidity):
        width = type(self).WIDTH
        height = type(self).HEIGHT

        image = Image.new("1", (width, height), 0)
        draw = ImageDraw.Draw(image)

        font = ImageFont.load_default()
        padding = -2
        top = padding
        bottom = height - padding
        draw.text((0, top + 0), "Visible: {}".format(visible), font=font, fill=255)
        draw.text((0, top + 10), "Infrared: {}".format(str(infrared)), font=font, fill=255)
        draw.text((0, top + 20), "Temp: {:0.2f} C".format(temp), font=font, fill=255)
        draw.text((0, top + 30), "Pressure: {:0.2f} hPa ".format(pressure), font=font, fill=255)
        draw.text((0, top + 40), "Humidity: {:0.2f} %".format(humidity), font=font, fill=255)

        self.disp.image(image)
        self.disp.display()

