"""app/apis/views/__init__.py
"""
from apis.views.motor import Raspi as RaspiMotor
from apis.views.servo import Raspi as RaspiServo

raspi_motor = RaspiMotor()
raspi_servo = RaspiServo()
