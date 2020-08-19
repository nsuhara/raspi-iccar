"""app/apis/views/motor.py
"""
import time

import RPi.GPIO as GPIO

GPIO_BCM_L293D_EN1 = 17
GPIO_BCM_L293D_IN1 = 27
GPIO_BCM_L293D_IN2 = 22


class Raspi():
    """Raspi
    """

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BCM_L293D_EN1, GPIO.OUT)
        GPIO.setup(GPIO_BCM_L293D_IN1, GPIO.OUT)
        GPIO.setup(GPIO_BCM_L293D_IN2, GPIO.OUT)
        GPIO.output(GPIO_BCM_L293D_EN1, GPIO.LOW)
        GPIO.output(GPIO_BCM_L293D_IN1, GPIO.LOW)
        GPIO.output(GPIO_BCM_L293D_IN2, GPIO.LOW)
        self.pwm_l293d_in1 = GPIO.PWM(GPIO_BCM_L293D_IN1, 50)
        self.pwm_l293d_in2 = GPIO.PWM(GPIO_BCM_L293D_IN2, 50)
        self.pwm_l293d_in1.start(0)
        self.pwm_l293d_in2.start(0)
        self.on = False
        print('using pin {}, {}, {}'.format(GPIO_BCM_L293D_EN1,
                                            GPIO_BCM_L293D_IN1, GPIO_BCM_L293D_IN2))
        print('pulse width modulation {} Hz'.format(50))

    def destroy(self):
        """destroy
        """
        self.stop()
        GPIO.cleanup()

    def start(self, button_type, button_option):
        """start
        """
        if self.on is True:
            print('skip button event')
            return
        if button_type == 'BUTTON_TYPE_UP':
            GPIO.output(GPIO_BCM_L293D_EN1, GPIO.HIGH)
            self.pwm_l293d_in1.ChangeDutyCycle(button_option)
            self.pwm_l293d_in2.ChangeDutyCycle(0)
            self.on = True
        elif button_type == 'BUTTON_TYPE_DOWN':
            GPIO.output(GPIO_BCM_L293D_EN1, GPIO.HIGH)
            self.pwm_l293d_in1.ChangeDutyCycle(0)
            self.pwm_l293d_in2.ChangeDutyCycle(button_option)
            self.on = True
        else:
            self.on = False

    def stop(self):
        """stop
        """
        GPIO.output(GPIO_BCM_L293D_EN1, GPIO.LOW)
        self.pwm_l293d_in1.ChangeDutyCycle(0)
        self.pwm_l293d_in2.ChangeDutyCycle(0)
        self.on = False

    def loop(self):
        """loop
        """
        while True:
            self.start('BUTTON_TYPE_UP', 50)
            print('>>> BUTTON_TYPE_UP')
            time.sleep(3)
            self.stop()
            print('>>> STOP')
            time.sleep(3)
            self.start('BUTTON_TYPE_DOWN', 50)
            print('>>> BUTTON_TYPE_DOWN')
            time.sleep(3)
            self.stop()
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
