FROM ubuntu:18.04
LABEL description="Virtuoso Universal Server (Open Source Edition)"
LABEL maintainer="Arnold Kuzniar"
LABEL email="a.kuzniar@esciencecenter.nl"
LABEL orcid="0000-0003-1711-7961"
LABEL version="0.1.0"

# update packages & install dependencies for Virtuoso
RUN apt-get update && \
    apt-get install -y \
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
      python-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -U pip six docopt

# add command-line args and set defaults
ARG VOS_VERSION=v7.2.8
ARG VOS_PREFIX=/usr/local/virtuoso-opensource
ARG VOS_SHARE=/tmp/share
ARG VOS_CFG_PARS="\
  URIQA:DefaultHost=localhost:8890 \
  HTTPServer:ServerPort=8890 \
  Parameters:ServerPort=1111 \
  Parameters:DirsAllowed=.,$VOS_PREFIX/share/virtuoso/vad,$VOS_SHARE \
  Parameters:MaxVectorSize=3000000 \
  Parameters:AdjustVectorSize=1 \
  Parameters:NumberOfBuffers=340000 \
  Parameters:MaxDirtyBuffers=250000 \
  SPARQL:ResultSetMaxRows=1000"

# set env variables
ENV PATH=${VOS_PREFIX}/bin:${PATH}
ENV VOS_SHARE=${VOS_SHARE}
ENV VOS_CFG_FILE=${VOS_PREFIX}/var/lib/virtuoso/db/virtuoso.ini

# compile Virtuoso including several VAD packages
WORKDIR /tmp
RUN git clone -b ${VOS_VERSION} https://github.com/openlink/virtuoso-opensource.git
WORKDIR /tmp/virtuoso-opensource
ENV CFLAGS="-O2 -m64"
RUN ./autogen.sh && \
    ./configure --prefix=${VOS_PREFIX} \
      --enable-conductor-vad \
      --enable-rdb2rdf-vad \
      --enable-rdfmappers-vad \
      --enable-fct-vad && \
    make -j $(nproc) && \
    make install
WORKDIR /tmp
RUN rm -fr virtuoso-opensource

# update Virtuoso config file
COPY src/update_config.py /tmp
RUN if [ "${VOS_CFG_PARS}" ]; then \
    python update_config.py -c ${VOS_CFG_FILE} ${VOS_CFG_PARS}; fi

# add volume for file sharing
VOLUME $VOS_SHARE
WORKDIR $VOS_SHARE

# expose HTTP and DB server ports
EXPOSE 8890 1111

# start Virtuoso server
CMD ["bash", "-c", "virtuoso-t +wait +foreground +configfile ${VOS_CFG_FILE}"]

HEALTHCHECK --interval=5s CMD curl --silent --fail localhost:8890 || exit 1
