import smbus2 as smbus
import time
import logging


logger = logging.getLogger(__name__)


# TSL2561

# Register addresses
REG_CONTROL         = 0x00
REG_TIMING          = 0x01
REG_THRESHLOWLOW    = 0x02
REG_THRESHLOWHIGH   = 0x03
REG_THRESHHIGHLOW   = 0x04
REG_THRESHHIGHHIGH  = 0x05
REG_INTERRUPT       = 0x06
REG_ID              = 0x0A
REG_DATA0LOW        = 0x0C
REG_DATA0HIGH       = 0x0D
REG_DATA1LOW        = 0x0E
REG_DATA1HIGH       = 0x0F

# The following values are bitwise ORed with register addresses to create a command value
SMB_BLOCK           = 0x10  # Transaction to use Block Write/Read protocol
SMB_WORD            = 0x20  # Transaction to use Word Write/Read protocol
SMB_CLEAR           = 0x40  # Clear any pending interrupt (self-clearing)
SMB_COMMAND         = 0x80  # Select command register


class LightSensor(object):

    INTEGRATION_TIME_13MS = 0x00
    INTEGRATION_TIME_101MS = 0x01
    INTEGRATION_TIME_402MS = 0x02

    GAIN_1X = 0x00
    GAIN_16X = 0x10

    CONTROL_POWER_UP = 0x03
    CONTROL_POWER_DOWN = 0x00

    def __init__(self, i2c_bus, i2c_address):
        self.bus = smbus.SMBus(i2c_bus)
        self.i2c_address = i2c_address
        self.set_integration_time_and_gain(type(self).INTEGRATION_TIME_402MS,
                                           type(self).GAIN_1X)

    def _power(self, val):
        self.bus.write_byte_data(self.i2c_address,
                                 REG_CONTROL | SMB_COMMAND,
                                 val)

    def _power_up(self):
        self._power(type(self).CONTROL_POWER_UP)

    def _power_down(self):
        self._power(type(self).CONTROL_POWER_DOWN)

    def set_integration_time_and_gain(self, integration_time, gain=GAIN_1X):
        self._power_up()
        self.bus.write_byte(self.i2c_address,
                            REG_TIMING | SMB_COMMAND,
                            integration_time | gain)

    def start(self):
        self._power_up()

    def read(self):
        ch0 = self.bus.read_i2c_block_data(self.i2c_address,
                                           REG_DATA0LOW | SMB_COMMAND | SMB_WORD, 2)
        ch1 = self.bus.read_i2c_block_data(self.i2c_address,
                                           REG_DATA1LOW | SMB_COMMAND | SMB_WORD, 2)
        logger.debug("ch0 {}".format(ch0))
        logger.debug("ch1 {}".format(ch1))
        v0 = ch0[1] * 256 + ch0[0]
        v1 = ch1[1] * 256 + ch1[0]
        visible = v0 - v1
        infrared = v1
        return visible, infrared


