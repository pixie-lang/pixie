FROM debian:sid

# install dependencies
RUN apt-get update \
    && apt-get install -y gcc g++ libboost-dev pkg-config make curl bzip2 python2.7 \
    && apt-get install -y libffi-dev libuv-dev libedit-dev

ADD . /usr/src/pixie

# build the thing
RUN cd /usr/src/pixie \
    && make PYTHON=python2.7 build_with_jit \
    && ln -s /usr/src/pixie/pixie-vm /usr/bin/pxi

ENTRYPOINT ["/usr/bin/pxi"]
