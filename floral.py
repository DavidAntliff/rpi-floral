#!/usr/bin/env python
import logging
import time

import light_sensor
import display
import bme280
import led


logger = logging.getLogger(__name__)

LIGHT_SENSOR_I2C_BUS = 1
LIGHT_SENSOR_I2C_ADDRESS = 0x39

DISPLAY_PIN_RESET = 24
DISPLAY_PIN_DC = 23
DISPLAY_SPI_PORT = 0
DISPLAY_SPI_DEVICE = 0

BME280_I2C_BUS = 1
BME280_I2C_ADDRESS = 0x76

LED_PIN_RED = 22
LED_PIN_GREEN = 20
LED_PIN_BLUE = 21


def main():
    logging.basicConfig(level=logging.INFO)
    ls = light_sensor.LightSensor(LIGHT_SENSOR_I2C_BUS, LIGHT_SENSOR_I2C_ADDRESS)
    di = display.Display(DISPLAY_PIN_RESET,
                         DISPLAY_PIN_DC,
                         DISPLAY_SPI_PORT,
                         DISPLAY_SPI_DEVICE)
    tph = bme280.BME280(BME280_I2C_BUS, BME280_I2C_ADDRESS)
    led0 = led.LED(LED_PIN_RED, LED_PIN_GREEN, LED_PIN_BLUE)

    while True:
        ls.start()
        time.sleep(0.5)
        visible, infrared = ls.read()
        temp, _, pressure, humidity = tph.read()
        di.update(visible, infrared, temp, pressure, humidity)

        #blue_value = (65535 - visible) / 65535.0 * 100
        #logger.info(blue_value)
        #led0.set_blue(blue_value)
        led0.set_blue(100)
        time.sleep(0.01)
        led0.set_blue(0)


if __name__ == '__main__':
    main()
