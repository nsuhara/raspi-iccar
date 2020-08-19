# Raspberry PiとPythonでリモコンカーを作成する

## はじめに

`Mac環境の記事ですが、Windows環境も同じ手順になります。環境依存の部分は読み替えてお試しください。`

### 目的

スマートフォンからWEBアプリのコントローラに繋ぎ、Wi-FI介してリモコンカーを制御します。ラジコンをインターネットで動かすイメージです。

この記事を最後まで読むと、次のことができるようになります。

| No.  | 概要             | キーワード       |
| :--- | :--------------- | :--------------- |
| 1    | 電子回路         |                  |
| 2    | REST API         | Flask            |
| 3    | コントローラ制御 | HTML, JavaScript |
| 4    | モータ制御       | モータGPIO       |
| 5    | サーボモータ制御 | サーボモータGPIO |

### 完成イメージ

|                                                                      コントローラ                                                                      |                                                                          本体                                                                           |
| :----------------------------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------: |
| <img width="300" alt="IMG_4765.PNG" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/8bcab943-9e4d-6860-1d6b-011a6f621176.png"> | <img width="300" alt="IMG_4762.JPG" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/777ca8a3-de57-cd9a-4319-86791f761942.jpeg"> |

### 実行環境

| 環境                           | Ver.    |
| :----------------------------- | :------ |
| macOS Catalina                 | 10.15.6 |
| Raspberry Pi 4 Model B 4GB RAM | -       |
| Raspberry Pi OS (Raspbian)     | 10      |
| Python                         | 3.7.3   |
| Flask                          | 1.1.1   |
| RPi.GPIO                       | 0.7.0   |

### ソースコード

実際に実装内容やソースコードを追いながら読むとより理解が深まるかと思います。是非ご活用ください。

[GitHub](https://github.com/nsuhara/raspi-iccar.git)

### 関連する記事

- [Raspberry PiのセットアップからPython環境のインストールまで](https://qiita.com/nsuhara/items/05a2b41d94ced1f54316)

## 電子回路

### モータ電子回路

<img width="700" alt="motor.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/06e680ee-890e-e2bb-9fdc-5a313d99a149.png">

### サーボモータ電子回路

<img width="700" alt="servo.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/93afe4d4-4f7b-9b27-a580-7e8edf56bc50.png">

## WEBアプリ構成

```target.sh
/
├── Dockerfiles
│   ├── app
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── entrypoint.sh
│   ├── docker_compose_up.sh
│   └── docker_run.sh
├── app
│   ├── __init__.py
│   ├── apis
│   │   ├── __init__.py
│   │   ├── client
│   │   │   ├── __init__.py
│   │   │   ├── post_motor.py
│   │   │   └── post_servo.py
│   │   ├── models
│   │   │   └── __init__.py
│   │   ├── static
│   │   │   └── __init__.py
│   │   ├── templates
│   │   │   └── app_form.html
│   │   └── views
│   │       ├── __init__.py
│   │       ├── api.py
│   │       ├── app.py
│   │       ├── handler.py
│   │       ├── motor.py
│   │       └── servo.py
│   ├── common
│   │   ├── __init__.py
│   │   └── utility.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── docker.py
│   │   ├── localhost.py
│   │   └── production.py
│   ├── requirements.txt
│   ├── run.py
│   └── tests
│       ├── __init__.py
│       └── test_apis.py
└── config
    ├── docker
    ├── localhost
    └── production
```

## REST API

```target.sh
/app
└─ apis
      └─ views
            └── handler.py
```

### REST APIハンドラー

```handler.py
"""app/apis/views/handler.py
"""
from flask import Blueprint, jsonify, request

from common.utility import err_response
from apis.views.api import handler as api_handler
from apis.views.app import handler as app_handler

apis = Blueprint(name='rasp-iccar', import_name=__name__,
                 url_prefix='/rasp-iccar')


@apis.route('/healthcheck', methods=['GET'])
def healthcheck():
    """healthcheck
    """
    return jsonify({'status': 'healthy'}), 200


@apis.route('/api', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api():
    """api
    """
    if request.method == 'GET':
        process = request.args.get('process')
        req = {
            'param1': request.args.get('request'),
            'param2': request.args
        }

        if process == 'back_end':
            return api_handler(req=req)

        if process == 'front_end':
            return app_handler(req=req)

    if request.method == 'POST' or request.method == 'PUT' or request.method == 'DELETE':
        payload = request.json
        process = payload.get('process')
        req = payload.get('request')

        if process == 'back_end':
            return api_handler(req=req)

    return jsonify({'message': 'no route matched with those values'}), 200


@apis.errorhandler(404)
@apis.errorhandler(500)
def errorhandler(error):
    """errorhandler
    """
    return err_response(error=error), error.code
```

## コントローラ制御

```target.sh
/app
└─ apis
      ├─ templates
      │    └── app_form.html
      └─ views
            └── app.py
```

### コントローラハンドラー

```app.py
"""app/apis/views/app.py
"""
from flask import jsonify, render_template


def handler(req):
    """handler
    """
    param1 = req.get('param1')
    param2 = req.get('param2')

    if param1 == 'app_form':
        return _app_form(req=param2)

    return jsonify({'message': 'no route matched with those values'}), 200


def _app_form(req):
    """_app_form
    """
    if req.get('secret_key', '') != 'M7XvWE9fSFg3':
        return jsonify({'message': 'no route matched with those values'}), 200
    return render_template('app_form.html')
```

### コントローラI/F

```app_form.html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>raspi-iccar</title>

    <style type="text/css">
        html,
        body {
            -webkit-user-select: none;
            width: 100%;
            height: 100%;
        }

        table {
            width: 100%;
            height: 100%;
        }

        table,
        td {
            border: 1px gray solid;
            padding: 10px;
        }

        button.up-down {
            touch-action: manipulation;
            font-size: 5vh;
            font-weight: bold;
            width: 45%;
            height: 95%;
        }

        button.right-left {
            touch-action: manipulation;
            font-size: 5vh;
            font-weight: bold;
            width: 95%;
            height: 50%;
        }

        .button_option {
            clip: rect(1px, 1px, 1px, 1px);
            position: absolute !important;
        }

        .button_option_label {
            font-weight: bold;
            font-size: 5vh;
        }

        .button_option:checked+.button_option_label {
            background: #4169e1;
            color: #fff;
        }
    </style>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script type="text/javascript">
        let lastTouchEndTime = 0;
        document.addEventListener('touchend', (event) => {
            const now = new Date().getTime();
            if ((now - lastTouchEndTime) < 350) {
                event.preventDefault();
            }
            lastTouchEndTime = now;
        });
    </script>
    <script type="text/javascript">
        // var HOST = "http://127.0.0.1:5000/rasp-iccar/api";
        var HOST = "http://192.168.0.77:5000/rasp-iccar/api";
        var BUTTON_TIMER_LONG = 500;
        var BUTTON_TIMER_REPEAT = 500;

        var up_down_timer_id;
        var right_left_timer_id;

        $(function () {
            var post = function (button_type, button_event, button_option) {
                var data = {
                    "process": "back_end",
                    "request": {
                        "param1": "button",
                        "param2": [{
                            "button_type": button_type,
                            "button_event": button_event,
                            "button_option": button_option
                        }]
                    }
                };

                $.ajax({
                    type: "post",
                    url: HOST,
                    data: JSON.stringify(data),
                    contentType: "application/json",
                    dataType: "json",
                    scriptCharset: "utf-8",
                    success: function (data) {
                        console.log(JSON.stringify(data));
                    },
                    error: function (data) {
                        console.log(JSON.stringify(data));
                    }
                });
            };

            var button_event_long = function (button_type, button_event, button_option, button_timer) {
                post(button_type, button_event, button_option);
                if (button_timer == "BUTTON_TIMER_UP_DOWN") {
                    clearTimeout(up_down_timer_id);
                    up_down_timer_id = setTimeout(button_event_repeat, BUTTON_TIMER_REPEAT, button_type, "BUTTON_EVENT_REPEAT", button_option, button_timer);
                } else {
                    clearTimeout(right_left_timer_id);
                    right_left_timer_id = setTimeout(button_event_repeat, BUTTON_TIMER_REPEAT, button_type, "BUTTON_EVENT_REPEAT", button_option, button_timer);
                }
            };

            var button_event_repeat = function (button_type, button_event, button_option, button_timer) {
                post(button_type, button_event, button_option);
                if (button_timer == "BUTTON_TIMER_UP_DOWN") {
                    clearTimeout(up_down_timer_id);
                    up_down_timer_id = setTimeout(button_event_repeat, BUTTON_TIMER_REPEAT, button_type, "BUTTON_EVENT_REPEAT", button_option, button_timer);
                } else {
                    clearTimeout(right_left_timer_id);
                    right_left_timer_id = setTimeout(button_event_repeat, BUTTON_TIMER_REPEAT, button_type, "BUTTON_EVENT_REPEAT", button_option, button_timer);
                }
            };

            // button up
            $("#button_up").on("mousedown touchstart", function () {
                var button_option = $('input[name="button_option"]:checked').val();
                post("BUTTON_TYPE_UP", "BUTTON_EVENT_PRESS", button_option);
                clearTimeout(up_down_timer_id);
                up_down_timer_id = setTimeout(button_event_long, BUTTON_TIMER_LONG, "BUTTON_TYPE_UP", "BUTTON_EVENT_LONG", button_option, "BUTTON_TIMER_UP_DOWN");
            }).on("mouseup mouseleave touchend", function () {
                clearTimeout(up_down_timer_id);
                post("BUTTON_TYPE_UP", "BUTTON_EVENT_RELEASE", 0)
            });

            // button down
            $("#button_down").on("mousedown touchstart", function () {
                var button_option = $('input[name="button_option"]:checked').val();
                post("BUTTON_TYPE_DOWN", "BUTTON_EVENT_PRESS", button_option);
                clearTimeout(up_down_timer_id);
                up_down_timer_id = setTimeout(button_event_long, BUTTON_TIMER_LONG, "BUTTON_TYPE_DOWN", "BUTTON_EVENT_LONG", button_option, "BUTTON_TIMER_UP_DOWN");
            }).on("mouseup mouseleave touchend", function () {
                clearTimeout(up_down_timer_id);
                post("BUTTON_TYPE_DOWN", "BUTTON_EVENT_RELEASE", 0)
            });

            // button right
            $("#button_right").on("mousedown touchstart", function () {
                post("BUTTON_TYPE_RIGHT", "BUTTON_EVENT_PRESS", -30);
                clearTimeout(right_left_timer_id);
                right_left_timer_id = setTimeout(button_event_long, BUTTON_TIMER_LONG, "BUTTON_TYPE_RIGHT", "BUTTON_EVENT_LONG", -30, "BUTTON_TIMER_RIGHT_LEFT");
            }).on("mouseup mouseleave touchend", function () {
                clearTimeout(right_left_timer_id);
                post("BUTTON_TYPE_RIGHT", "BUTTON_EVENT_RELEASE", 0)
            });

            // button left
            $("#button_left").on("mousedown touchstart", function () {
                post("BUTTON_TYPE_LEFT", "BUTTON_EVENT_PRESS", 35);
                clearTimeout(right_left_timer_id);
                right_left_timer_id = setTimeout(button_event_long, BUTTON_TIMER_LONG, "BUTTON_TYPE_LEFT", "BUTTON_EVENT_LONG", 35, "BUTTON_TIMER_RIGHT_LEFT");
            }).on("mouseup mouseleave touchend", function () {
                clearTimeout(right_left_timer_id);
                post("BUTTON_TYPE_LEFT", "BUTTON_EVENT_RELEASE", 0)
            });
        })
    </script>
</head>

<body>
    <table>
        <tr height="20%">
            <td colspan="2">
                <table>
                    <tr align="center">
                        <td>
                            <input class="button_option" type="radio" id="button_high" name="button_option"
                                value="100" />
                            <label class="button_option_label" for="button_high">はやい</label>
                        </td>
                        <td>
                            <input class="button_option" type="radio" id="button_middle" name="button_option" value="50"
                                checked />
                            <label class="button_option_label" for="button_middle">ふつう</label>
                        </td>
                        <td>
                            <input class="button_option" type="radio" id="button_low" name="button_option" value="25" />
                            <label class="button_option_label" for="button_low">おそい</label>
                        </td>
                </table>
            </td>
        </tr>
        <tr>
            <td width="50%">
                <table>
                    <tr align="center">
                        <td width="50%" valign="bottom"><button class="up-down" type="button"
                                id="button_up">↑<br>まえ</button></td>
                    </tr>
                    <tr align="center">
                        <td valign="top"><button class="up-down" type="button" id="button_down">↓<br>うしろ</button></td>
                    </tr>
                </table>
            </td>
            <td>
                <table>
                    <tr align="center">
                        <td width="50%" align="right"><button class="right-left" type="button"
                                id="button_left">←<br>ひだり</button></td>
                        <td align="left"><button class="right-left" type="button" id="button_right">→<br>みぎ</button>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>

</html>
```

## モータ制御

```target.sh
/app
└─ apis
      └─ views
            ├── __init__.py
            ├── api.py
            └── motor.py
```

### モータハンドラー

```__init__.py
"""app/apis/views/__init__.py
"""
from apis.views.motor import Raspi as RaspiMotor
from apis.views.servo import Raspi as RaspiServo

raspi_motor = RaspiMotor()
raspi_servo = RaspiServo()
```

```api.py
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
```

### モータGPIO

```motor.py
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
```

## サーボモータ制御

```target.sh
/app
└─ apis
      └─ views
            ├── __init__.py
            ├── api.py
            └── servo.py
```

### サーボモータハンドラー

```__init__.py
"""app/apis/views/__init__.py
"""
from apis.views.motor import Raspi as RaspiMotor
from apis.views.servo import Raspi as RaspiServo

raspi_motor = RaspiMotor()
raspi_servo = RaspiServo()
```

```api.py
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
```

### サーボモータGPIO

```servo.py
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
```
