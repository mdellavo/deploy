FROM python:3.9

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /gordy

RUN apt-get update
RUN apt-get install git openssh-client openssl

RUN git clone https://github.com/mdellavo/gordy.git /gordy
RUN apt-get install -y libolm-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get purge -y git openssh-client
RUN apt-get autoremove -y

RUN useradd -ms /bin/bash gordy
USER gordy

ENTRYPOINT ["python3", "-m", "gordy"]
