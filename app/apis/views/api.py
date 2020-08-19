"""app/apis/views/api.py
"""
from flask import jsonify

from apis.views import raspi_motor, raspi_servo


def handler(req):
    """handler
    """
    param1 = req.get('param1')
    param2 = req.get('param2')

    if param1 == 'button':
        return _button(payloads=param2[0])

    return jsonify({'message': 'no route matched with those values'}), 200


def _button(payloads):
    """_button
    """
    button_type = payloads.get('button_type')
    button_event = payloads.get('button_event')
    button_option = payloads.get('button_option')

    if button_type in ['BUTTON_TYPE_UP', 'BUTTON_TYPE_DOWN']:
        _motor(button_type, button_event, int(button_option))
    elif button_type in ['BUTTON_TYPE_RIGHT', 'BUTTON_TYPE_LEFT']:
        _servo(button_event, int(button_option))

    response = {
        'status': 'success',
        'request': payloads
    }
    print(response)
    return jsonify(response), 200


def _servo(button_event, button_option):
    """_servo
    """
    if button_event in ['BUTTON_EVENT_PRESS', 'BUTTON_EVENT_LONG', 'BUTTON_EVENT_REPEAT']:
        return _servo_on(button_option)
    return _servo_off(button_option)


def _servo_on(button_option):
    """_servo_on
    """
    raspi_servo.start(button_option)


def _servo_off(button_option):
    """_servo_off
    """
    raspi_servo.stop(button_option)


def _motor(button_type, button_event, button_option):
    """_motor
    """
    if button_event in ['BUTTON_EVENT_PRESS', 'BUTTON_EVENT_LONG', 'BUTTON_EVENT_REPEAT']:
        return _motor_on(button_type, button_option)
    return _motor_off()


def _motor_on(button_type, button_option):
    """_motor_on
    """
    raspi_motor.start(button_type, button_option)


def _motor_off():
    """_motor_off
    """
    raspi_motor.stop()
