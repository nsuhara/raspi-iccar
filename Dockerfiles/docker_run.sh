#!/bin/sh

docker stop $(docker ps -q)
docker rm $(docker ps -q -a)
# docker rmi $(docker images -q) -f

rsync -av --exclude=app/tests* app Dockerfiles/app

docker build -t rasp-iccar Dockerfiles/app
docker run -it -p 5000:5000 rasp-iccar:latest
