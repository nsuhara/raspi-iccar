# rasp-iccar

## api

| service     | method                 | example                 |
| :---------- | :--------------------- | :---------------------- |
| healthcheck | get                    | /rasp-iccar/healthcheck |
| api         | get, post, put, delete | /rasp-iccar/api         |

## api sample

| service | method | example                               |
| :------ | :----- | :------------------------------------ |
| motor   | post   | [link](app/apis/client/post_motor.py) |
| servo   | post   | [link](app/apis/client/post_servo.py) |

## app sample

| service  | method | example                                                                    |
| :------- | :----- | :------------------------------------------------------------------------- |
| app form | get    | /rasp-iccar/api?process=front_end&request=app_form&secret_key=M7XvWE9fSFg3 |

## setup environment

```command_line.sh
source config/{environment}
```

## check code

```command_line.sh
python -B -m pylint --rcfile=.pylintrc -f parseable `find app -name "*.py" -not -path "app/tests"`
```

## unit test

```command_line.sh
python -B -m unittest discover tests
```

## launch docker

```command_line.sh
Dockerfiles/docker_compose_up.sh
```

## launch flask

```command_line.sh
source config/{environment}
flask run --host=0.0.0.0 --port=5000
```
