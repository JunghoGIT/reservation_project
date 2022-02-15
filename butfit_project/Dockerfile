FROM ubuntu:18.04


RUN apt-get -y update && apt-get -y dist-upgrade

RUN apt-get install -y apt-utils dialog libpq-dev

RUN apt-get install -y python3-pip python3-dev

ENV PYTHONUNBUFFERED=0

ENV PYTHONIOENCODING=utf-8

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools

RUN mkdir /config

ADD /config/requirements.txt /config/

RUN pip3 install -r /config/requirements.txt


WORKDIR /ButFit