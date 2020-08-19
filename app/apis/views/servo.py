"""app/apis/views/servo.py
"""
import time

import RPi.GPIO as GPIO

GPIO_BCM_SERVO = 18


class Raspi():
    """Raspi
    """

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BCM_SERVO, GPIO.OUT)
        GPIO.output(GPIO_BCM_SERVO, GPIO.LOW)
        self.pwm_servo = GPIO.PWM(GPIO_BCM_SERVO, 50)
        self.pwm_servo.start(0)
        self.on = False
        print('using pin {}'.format(GPIO_BCM_SERVO))
        print('pulse width modulation {} Hz'.format(50))

    def destroy(self):
        """destroy
        """
        self.pwm_servo.stop()
        GPIO.cleanup()

    def angle(self, angle):
        """angle
        """
        duty = 2.5 + (12.0 - 2.5) * (angle + 90) / 180
        self.pwm_servo.ChangeDutyCycle(duty)

    def start(self, angle):
        """start
        """
        if self.on is True:
            print('skip button event')
            return
        self.angle(angle)
        self.on = True

    def stop(self, angle):
        """stop
        """
        self.angle(angle)
        self.on = False

    def loop(self):
        """loop
        """
        while True:
            self.start(-30)
            print('>>> BUTTON_TYPE_RIGHT')
            time.sleep(3)
            self.stop(0)
            print('>>> STOP')
            time.sleep(3)
            self.start(35)
            print('>>> BUTTON_TYPE_LEFT')
            time.sleep(3)
            self.stop(0)
            print('>>> STOP')
            time.sleep(3)


if __name__ == '__main__':
    raspi = Raspi()
    try:
        print('start')
        raspi.loop()
    except KeyboardInterrupt:
        raspi.destroy()
        print('stop')
