FROM ubuntu:18.04 
LABEL mainter "shin-ch13"

# set timezone
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install basic packages and usuful packages
RUN apt update && apt install -y \
    kmod git autoconf automake libtool make gawk libreadline-dev \
	texinfo dejagnu pkg-config libpam0g-dev libjson-c-dev bison flex \
	libc-ares-dev libsystemd-dev libgmp-dev \
    python3-dev python3-pip python-pytest python3-jinja2 \
    vim git tmux silversearcher-ag bash-completion

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
 && echo "fi" >> ~/.bashrc \