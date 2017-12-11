# Virtuoso Universal Server (OSE)
#

FROM ubuntu:16.04
LABEL description="Virtuoso Universal Server (OSE)"
LABEL maintainer="Arnold Kuzniar"
LABEL email="a.kuzniar@esciencecenter.nl"
LABEL version="0.1"

# update packages & install dependencies for Virtuoso
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    automake \
    gperf \
    gawk \
    libtool \
    flex \
    bison \
    libssl-dev \
    net-tools \
    vim \
    curl \
    python \
    python-pip \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -U pip docopt

# add command-line args and set defaults
ARG VOS_VERSION=stable/7
ARG VOS_PREFIX=/usr/local/virtuoso-opensource
ARG VOS_PARAMS

# compile & install Virtuoso including serveral VAD packages
WORKDIR /tmp
RUN git clone -b ${VOS_VERSION} https://github.com/openlink/virtuoso-opensource.git
WORKDIR /tmp/virtuoso-opensource
ENV CFLAGS="-O2 -m64"
RUN ./autogen.sh && ./configure --prefix=${VOS_PREFIX} \
    --enable-conductor-vad \
    --enable-rdb2rdf-vad \
    --enable-rdfmappers-vad \
    --enable-fct-vad \
    && make -j $(nproc) && make install
WORKDIR /tmp
RUN rm -fr virtuoso-opensource

# add Virtuoso binaries to PATH
ENV PATH=${VOS_PREFIX}/bin:${PATH}

# update Virtuoso config file (if VOS_PARAMS not empty)
ENV VOS_CFG_FILE=${VOS_PREFIX}/var/lib/virtuoso/db/virtuoso.ini
COPY update_config.py /tmp
RUN if [ "$VOS_PARAMS" ]; then \
      python update_config.py -c ${VOS_CFG_FILE} ${VOS_PARAMS} ; fi

# add volume for file sharing
VOLUME /tmp/share
WORKDIR /tmp/share

# expose (default) Virtuoso server ports
EXPOSE 8890
EXPOSE 1111

# start Virtuoso server
CMD ["sh", "-c", "virtuoso-t +wait +foreground +configfile ${VOS_CFG_FILE}"]
