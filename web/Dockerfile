FROM python:3.6-alpine

RUN apk update && apk add build-base postgresql-dev

ENV FLASK_APP familytree.py
ENV FLASK_CONFIG docker

RUN adduser -D familytree
USER familytree

WORKDIR /home/familytree

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY familytree.py config.py boot.sh ./

EXPOSE 8000
ENTRYPOINT ["./boot.sh"]