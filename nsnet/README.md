# Nsnet

Nsnet creat docker container enviroment with flexible network.

## Host Requirement

* OS: `Ubuntu 18.04.6 LTS`
* Do not reference iptables from the bridge
  * ex1: `$ sudo sysctl -w net.bridge.bridge-nf-call-iptables=0`
  * ex2: `$ iptables -I FORWARD -m physdev --physdev-is-bridged -j ACCEPT`
* Python: 3.6.9
  * ex: `$ pyenv install 3.6.9 && pyenv local 3.6.9`

## Install & Setup

```shell
$ git clone https://github.com/shin-ch13/network-lab.git && cd nsnet
# install
$ sudo python3 setup.py install
or 
$ sudo pip3 install -e .
# uninstall
$ sudo rm /usr/local/lib/python3.6/dist-packages/nsnet-*
$ sudo rm /usr/local/bin/nsnet
$ sudo rm /usr/local/lib/python3.6/dist-packages/link_dokcer_ns-*
$ sudo rm /usr/local/bin/link-dokcer-ns
```

## Usage

```shell
usage: nsnet [-h] {create,recreate,destroy,shell} ...

Nsnet creat docker container with flexible network

positional arguments:
  {create,recreate,destroy,shell}
    create              Create and start nsnet
    recreate            Recreate and restart nsnet
    destroy             Stop and remove nsnet
    shell               Shell connect container

optional arguments:
  -h, --help            show this help message and exit
```

## Run Example

```shell
$ cd nsnet/test/simple_network
### create docker container enviroment with flexible network
$ sudo nsnet create -cf docker-compose.yml -nf net.yaml
### test or develop container enviroment
### "node1" is service name in docker-compose.yml
$ sudo nsnet shell node1
### after edit docker-compose.yml or net.yaml
$ sudo nsnet recreate
### destroy docker container enviroment
sudo nsnet destroy
```

## Links

* <https://github.com/buzz66boy/YNTDL/tree/master/resources>
* <https://nmstate.io/examples.html#interfaces-ethernet>
* <https://qiita.com/zen3/items/757f96cbe522a9ad397d>
* <https://docs.openstack.org/project-deploy-guide/tripleo-docs/latest/features/custom_networks.html>
* <https://access.redhat.com/documentation/ja-jp/red_hat_openstack_platform/14/html/advanced_overcloud_customization/custom-network-interface-templates>
* <https://www.maytry.net/how-to-use-yaml/>
* <https://www.task-notes.com/entry/20150922/1442890800>
* <https://www.lifewithpython.com/2013/06/pyyaml.html>
* <https://github.com/Grokzen/pykwalify/blob/master/docs/validation-rules.rst>
* <https://docs.python.org/ja/3.7/library/ipaddress.html>
