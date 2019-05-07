#!/usr/bin/env python
import time
import logging
from random import randint

import Adafruit_SSD1306
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from floral import (DISPLAY_PIN_RESET,
                    DISPLAY_PIN_DC,
                    DISPLAY_SPI_PORT,
                    DISPLAY_SPI_DEVICE,
                    LED_PIN_RED,
                    LED_PIN_GREEN,
                    LED_PIN_BLUE)


logger = logging.getLogger(__name__)

# https://github.com/e-ale/floral-bonnet-testkit/blob/master/button.py
GPIO_BUTTON = 4


# TODO:
#  - seems to be a single pixel that counts as a collision at top and bottom of pillars
#    especially when the top column is just off-screen and bird is at y = 0
#  - multiple pillars
#  - speed up
#  - intro screen


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "{}, {}".format(self.x, self.y)


class Display(object):

    WIDTH = 128
    HEIGHT = 64

    def __init__(self, reset_pin, dc_pin, spi_port, spi_device):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=reset_pin, dc=dc_pin,
                                                    spi=SPI.SpiDev(spi_port, spi_device, max_speed_hz=8000000))
        self.disp.begin()
        self.clear()

    def clear(self):
        self.disp.clear()
        self.disp.display()

    def render(self, image):
        self.disp.image(image)
        self.disp.display()


class Bird(object):
    def __init__(self, x, y):
        self.image = Image.open("bird.png")
        self.width = self.image.width
        self.height = self.image.height
        self.x = x
        self.y = y
        self.y_vel = -5.0

    def __str__(self):
        return "x {}, y {}, width {}, height {}, y_vel {}".format(
            self.x, self.y, self.width, self.height, self.y_vel)

    def blit_to(self, image):
        image.paste(self.image, (self.x, self.y))

    @property
    def top_right(self):
        return Point(self.x + self.width, self.y)

    @property
    def bottom_left(self):
        return Point(self.x, self.y + self.height)

    def flap(self):
        self.y_vel = -5.0

    def update(self):
        self.y = int(round(self.y + self.y_vel))
        self.y_vel += 1.0

        if self.y < 0:
            self.y = 0
        if self.y > 64:
            self.y = 64


class Pillar(object):
    def __init__(self, x, y, inverted=False):
        self.image = Image.open("pillar.png")
        self.width = self.image.width
        self.height = self.image.height
        self.x = x
        self.y = y
        self.x_vel = -2.0
        self.active = True
        if inverted:
            self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)

    def __str__(self):
        return "x {}, y {}, width {}, height {}".format(self.x, self.y, self.width, self.height)

    def blit_to(self, image):
        if self.active:
            image.paste(self.image, (self.x, self.y))

    @property
    def top_right(self):
        return Point(self.x + self.width, self.y)

    @property
    def bottom_left(self):
        return Point(self.x, self.y + self.height)

    def update(self):
        if self.active:
            self.x = int(round(self.x + self.x_vel))
            if self.x < 0 - self.width:
                self.active = False


def collide(a, b):
    # https://stackoverflow.com/a/40795835/143397
    # print("------")
    # print(a.top_right)
    # print(a.bottom_left)
    # print(b.top_right)
    # print(b.bottom_left)
    # print(a.top_right.x < b.bottom_left.x)
    # print(a.bottom_left.x > b.top_right.x)
    # print(a.top_right.y > b.bottom_left.y)
    # print(a.bottom_left.y < b.top_right.y)
    return not (a.top_right.x < b.bottom_left.x or
                a.bottom_left.x > b.top_right.x or
                a.top_right.y > b.bottom_left.y or
                a.bottom_left.y < b.top_right.y)


def main():
    logging.basicConfig(level=logging.INFO)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    di = Display(DISPLAY_PIN_RESET,
                 DISPLAY_PIN_DC,
                 DISPLAY_SPI_PORT,
                 DISPLAY_SPI_DEVICE)

    font = ImageFont.load_default()

    while True:
        bird = Bird(0, di.HEIGHT / 2)
        pillars = []

        last_state = True
        game_over = False
        gap_size = 32
        score = -1

        while not game_over:

            input_state = GPIO.input(GPIO_BUTTON)
            if last_state and not input_state:
                bird.flap()
            last_state = input_state

            bird.update()
            for pillar in pillars:
                pillar.update()
                if pillar.active and collide(bird, pillar):
                    print("bird {} hit pillar {}".format(str(bird), str(pillar)))
                    game_over = True
                if bird.y >= di.HEIGHT:
                    print("bird {} fell".format(str(bird)))
                    game_over = True

            pillars[:] = [x for x in pillars if x.active]

            if not pillars:
                height = randint(gap_size, di.HEIGHT - 1)
                pillar = Pillar(di.WIDTH, height, inverted=False)
                pillars.append(pillar)
                pillars.append(Pillar(pillar.x, pillar.y - pillar.height - gap_size, inverted=True))
                gap_size -= 1
                score += 1

            image = Image.new("1", (di.WIDTH, di.HEIGHT), 0)
            for pillar in pillars:
                pillar.blit_to(image)
            bird.blit_to(image)

            draw = ImageDraw.Draw(image)
            draw.text((di.WIDTH - 20, 2), "{}".format(score), font=font, fill=255)

            di.render(image)


            #time.sleep(1/50.0)

        image = Image.new("1", (di.WIDTH, di.HEIGHT), 0)
        draw = ImageDraw.Draw(image)
        draw.text((30, 20), "Game Over!", font=font, fill=255)
        draw.text((di.WIDTH - 20, 2), "{}".format(score), font=font, fill=255)
        di.render(image)

        while GPIO.input(GPIO_BUTTON):
            pass

if __name__ == '__main__':
    main()
