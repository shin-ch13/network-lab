FROM ubuntu:18.04 
LABEL mainter "shin-ch13"

ARG DEBIAN_FRONTEND=noninteractive
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

# set timezone
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install basic packages and usuful packages
RUN apt update && apt install -y \
    kmod git autoconf automake libtool make gawk libreadline-dev \
	texinfo dejagnu pkg-config libpam0g-dev libjson-c-dev bison flex \
	libc-ares-dev libsystemd-dev libgmp-dev \
    python3-dev python3-pip python-pytest python3-jinja2 python3-sphinx \
    install-info build-essential libsnmp-dev perl libcap-dev \
    libelf-dev libunwind-dev vim tmux silversearcher-ag bash-completion lsb-release sudo

# install network packages
RUN apt update && apt install -y \
    iproute2 mtr traceroute iputils-ping telnet iperf tcpdump \
    openvswitch-switch wget curl pppoe pppoeconf lldpd \
    iptables ethtool python-scapy netcat-openbsd \
    openssl gperf bridge-utils

# enable bash completion in interactive shells
RUN echo "" > ~/.bashrc \
 && echo "if ! shopt -oq posix; then" >> ~/.bashrc \
 && echo "  if [ -f /usr/share/bash-completion/bash_completion ]; then" >> ~/.bashrc \
 && echo "    . /usr/share/bash-completion/bash_completion" >> ~/.bashrc \
 && echo "  elif [ -f /etc/bash_completion ]; then" >> ~/.bashrc \
 && echo "    . /etc/bash_completion" >> ~/.bashrc \
 && echo "  fi" >> ~/.bashrc \
 && echo "fi" >> ~/.bashrc 

# https://deb.frrouting.org/
RUN curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add - \
 && FRRVER="frr-8" \
 && echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) $FRRVER | tee -a /etc/apt/sources.list.d/frr.list

# frr install
RUN apt update && apt install -y frr frr-pythontools

# frr deamon config state=yes
RUN sed -i -e 's/=no/=yes/g' /etc/frr/daemons

# latest linux-modules-extra-<kernel-version> package install
RUN apt install -y linux-modules-extra-`uname -r`

COPY ./docker-start /usr/sbin/docker-start
RUN chmod +x /usr/sbin/docker-start
ENTRYPOINT ["/usr/sbin/docker-start"]