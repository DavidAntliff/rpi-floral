import RPi.GPIO as GPIO


class LED(object):
    def __init__(self, red_pin, green_pine, blue_pin):
        self.red_pin = red_pin
        self.green_pin = green_pine
        self.blue_pin = blue_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.red_pin, GPIO.OUT)
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)

        # choosing a frequency for pwm
        pwm_freq = 100

        self.red_pwm_pin = GPIO.PWM(self.red_pin, pwm_freq)
        self.green_pwm_pin = GPIO.PWM(self.green_pin, pwm_freq)
        self.blue_pwm_pin = GPIO.PWM(self.blue_pin, pwm_freq)

        self.reset()

    def reset(self, r=0, g=0, b=0):
        self.red_pwm_pin.start(r)
        self.green_pwm_pin.start(g)
        self.blue_pwm_pin.start(b)

    def set_red(self, value):
        self.red_pwm_pin.ChangeDutyCycle(value)

    def set_green(self, value):
        self.green_pwm_pin.ChangeDutyCycle(value)

    def set_blue(self, value):
        self.blue_pwm_pin.ChangeDutyCycle(value)
