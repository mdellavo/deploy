FROM python:3.9

WORKDIR /site

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /rogue

RUN apt install git openssh-client openssl
RUN git clone https://github.com/mdellavo/rogue.git /rogue

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt purge -y git openssh-client
RUN apt autoremove -y

RUN useradd -ms /bin/bash rogue
USER rogue

EXPOSE 6543

ENTRYPOINT ["python3", "-m", "rogue"]
