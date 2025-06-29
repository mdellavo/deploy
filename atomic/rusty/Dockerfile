FROM rust

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /rusty

RUN apt install git openssh-client openssl
RUN git clone https://github.com/mdellavo/rusty.git /rusty

RUN cargo install --path .

RUN apt purge -y git openssh-client
RUN apt autoremove -y

ENTRYPOINT ["rusty"]
