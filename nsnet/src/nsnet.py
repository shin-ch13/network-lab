#!/usr/bin/env python3
import sys
import os
import pprint
import argparse
import yaml
import subprocess
import ipaddress
import collections
import nsnet_schema
from dockercmd_module import DockerCommand
from get_module_logger import *
from pykwalify.core import Core

logger = get_module_logger()

class Nsnet:
  def __init__(self):
    self.prefix = None
    self.composefile = None
    self.netfile = None
    self.data = None
    self.create_cmd = {}
    self.destroy_cmd = {}
    self.create_node_cmd = {}

  def load_netfile(self):
    logger.info('network yaml file Loading...')

    with open(self.netfile) as file:
      self.data = yaml.safe_load(file)

    c = Core(source_data=self.data, schema_data=yaml.safe_load(nsnet_schema.schema))
    c.validate(raise_exception=True)

    return logger.info('network yaml file Loaded')

  def check_netfile(self):
    logger.info('network yaml file Checking...')
    #namespaces_info = self.get_namespace()
    nodes_info = {}
    for network,network_detail in self.data['networks'].items():
      if network_detail['members'] == None:
        logger.error('{}: "members" requires one or more member'.format(network))
        sys.exit(1)
      elif network_detail['conn'] == 'direct' and len(network_detail['members']) != 2:
        logger.error('{}: "conn: {}" requires only two members'.format(network,network_detail['conn']))
        sys.exit(1)

      nodes = []
      addresses = []
      for member in network_detail['members']:
        if member['name'] not in nodes:
          nodes.append(member['name'])
          nodes_info.setdefault(member['name'], []).append(member['iface'])
        else:
          logger.error('{}: "members: {}" duplicate in members'.format(network,member['name']))
          sys.exit(1)
        if 'ip' in member:
          for ip in member['ip']:
            try:
              ipaddress.ip_interface(ip)
            except Exception as e:
              logger.error(e, file=sys.stderr)
              sys.exit(1)
            if ipaddress.ip_interface(ip) not in addresses:
              addresses.append(ipaddress.ip_interface(ip))
            else:
              logger.error('{}: "ip: {}" duplicate in members'.format(network,ipaddress.ip_interface(ip)))
              sys.exit(1)

    #if not (set(nodes_info.keys()) <=  set(namespaces_info.keys()) and len(namespaces_info.keys()) !=  0):
    #  logger.error('"{}" is not found in namespaces'.format(list(set(nodes_info.keys())-set(namespaces_info))))
    #  sys.exit(1)

    if not set(nodes_info.keys()) <=  set(DockerCommand().get_container_service('ALL')):
      logger.error('"{}" is not found in services'.format(list(set(nodes_info.keys())-set(DockerCommand().get_container_service('ALL')))))
      sys.exit(1)
    for node,ifaces in nodes_info.items():
      if len(ifaces) != len(set(ifaces)):
        logger.error('"{}" duplicate in "{}"'.format([k for k, v in collections.Counter(ifaces).items() if v > 1],node))
        sys.exit(1)
      #elif set(ifaces)-set(namespaces_info[node]) != set(ifaces):
      #  logger.error('"{}" aleready exist in "{}" namespace'.format(list(set(namespaces_info[node])-(set(namespaces_info[node])-set(ifaces))),node))
      #  sys.exit(1)

    for node,cmds in self.data['commands'].items():
      if node not in DockerCommand().get_container_service('ALL'):
        logger.error('commands: "{}" is not found in services'.format(node))
        sys.exit(1)

    return logger.info('network yaml file Checked')
  
  #def get_namespace(self):
  #  proc = subprocess.run("ip netns | awk '{ print $1 }'",stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
  #  if proc.returncode == 0:
  #    nodes = proc.stdout.decode('utf8').split()
  #  else:
  #    logger.error('{}'.format(proc.stderr.decode('utf8')))
  #    sys.exit(1)
  #  ifaces = []
  #  for name in nodes:
  #    proc = subprocess.run(['ip','netns','exec',name,'ls','/sys/class/net/'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  #    if proc.returncode == 0:
  #      ifaces.append(proc.stdout.decode('utf8').split())
  #    else:
  #      logger.error('{}'.format(proc.stderr.decode('utf8')))
  #      sys.exit(1)
  #  
  #  return dict(zip(nodes,ifaces))

  def read_netfile(self):
    logger.info('network yaml file Reading...')
    self.check_netfile()

    for network,network_detail in self.data['networks'].items():
      if network_detail['conn'] == 'direct':
        self.create_cmd.setdefault(network, []).append('ip link add {} netns {} type veth peer name {} netns {}'.format(
          network_detail['members'][0]['iface'],
          network_detail['members'][0]['name'],
          network_detail['members'][1]['iface'],
          network_detail['members'][1]['name']
        ))
        self.destroy_cmd.setdefault(network, []).append('ip netns exec {} ip link delete dev {}'.format(
          network_detail['members'][0]['name'],
          network_detail['members'][0]['iface']
        ))
      elif network_detail['conn'] == 'bridge':
        self.create_cmd.setdefault(network, []).append('ip netns add {}-{}-br'.format(
          self.prefix,
          network
        ))
        self.create_cmd.setdefault(network, []).append('ip netns exec {}-{}-br ip link add name br0 type bridge'.format(
          self.prefix,
          network
        ))
        self.create_cmd.setdefault(network, []).append('ip netns exec {}-{}-br ip link set dev br0 up'.format(
          self.prefix,
          network
        ))
        self.destroy_cmd.setdefault(network, []).append('ip netns del {}-{}-br'.format(
          self.prefix,
          network
        ))
      for member in network_detail['members']:
        if network_detail['conn'] == 'direct':
          self.create_cmd.setdefault(network, []).append('ip netns exec {} ip link set {} up'.format(
            member['name'],
            member['iface']
          ))    
        elif network_detail['conn'] == 'bridge':
          self.create_cmd.setdefault(network, []).append('ip link add name {} netns {} type veth peer name br-{}-{} netns {}-{}-br'.format(
            member['iface'],
            member['name'],
            member['name'],
            member['iface'],
            self.prefix,
            network
          ))
          self.create_cmd.setdefault(network, []).append('ip netns exec {} ip link set {} up'.format(
            member['name'],
            member['iface']
          )) 
          self.create_cmd.setdefault(network, []).append('ip netns exec {}-{}-br ip link set br-{}-{} up'.format(
            self.prefix,
            network,
            member['name'],
            member['iface']
          ))
          self.create_cmd.setdefault(network, []).append('ip netns exec {}-{}-br ip link set dev br-{}-{} master br0 up'.format(
            self.prefix,
            network,
            member['name'],
            member['iface']
          ))
          self.destroy_cmd.setdefault(network, []).append('ip netns exec {} ip link delete dev {}'.format(
            member['name'],
            member['iface']
          ))
        if 'ip' in member:
          for ip in  member['ip']:
            if ipaddress.ip_interface(ip).version == 4:
              self.create_cmd.setdefault(network, []).append('ip netns exec {} ip addr add {} dev {}'.format(
                member['name'],
                ipaddress.ip_interface(ip),
                member['iface']
              ))
            elif ipaddress.ip_interface(ip).version == 6:
              self.create_cmd.setdefault(network, []).append('ip netns exec {} ip -6 addr add {} dev {}'.format(
                member['name'],
                ipaddress.ip_interface(ip),
                member['iface']
              ))
            #print(
            #  network, network_detail['conn'],
            #  member['name'],
            #  member['iface']
            #  ipaddress.ip_interface(ip),'v' + str(ipaddress.ip_interface(ip).version)
            #)
    
    for node,cmds in self.data['commands'].items():
      for cmd in cmds:
        self.create_node_cmd.setdefault(node, []).append('docker-compose exec {} sh -c "{}"'.format(
          node,
          cmd['cmd']
        ))

    return logger.info('network yaml file Readed')

  def create_container(self):
    logger.info('Docker Container Creating and Starting...')
    proc = subprocess.run(['docker-compose','-f',self.composefile,'up','-d'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      for log in proc.stderr.decode('utf8').split('\n'): logger.info(log)
      proc = subprocess.run(['docker-compose','ps'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      for log in proc.stdout.decode('utf8').split('\n'): logger.info(log)
    else:
      for log in proc.stderr.decode('utf8').split('\n'): logger.error(log)
      sys.exit(1)
    
    proc = subprocess.run(['link-dokcer-ns','link-on'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      for log in proc.stdout.decode('utf8').split('\n'): logger.info(log)
    else:
      for log in proc.stderr.decode('utf8').split('\n'): logger.error(log)
      sys.exit(1)
    
    return logger.info('Docker Container Created and Started')
    
  def destroy_container(self):
    logger.info('Docker Container Stoping and Removing...')

    proc = subprocess.run(['docker-compose','down'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      for log in proc.stderr.decode('utf8').split('\n'): logger.info(log)
      proc = subprocess.run(['docker-compose','ps'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      for log in proc.stdout.decode('utf8').split('\n'): logger.info(log)
    else:
      for log in proc.stderr.decode('utf8').split('\n'): logger.error(log)
      sys.exit(1)

    proc = subprocess.run(['link-dokcer-ns','link-off'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      for log in proc.stdout.decode('utf8').split('\n'): logger.info(log)
    else:
      for log in proc.stderr.decode('utf8').split('\n'): logger.error(log)
      sys.exit(1)

    return logger.info('Docker Container Stopped and Removed')

  def create_network(self):
    logger.info('Network create commands Executing...')

    for network,cmds in self.create_cmd.items():
      logger.info('Network {} Creating...'.format(network))
      for cmd in cmds:
        proc = subprocess.run(cmd,stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        if proc.returncode == 0:
          logger.info('command: {}'.format(cmd))
        else:
          logger.error('{}: {}'.format(network,cmd))
          logger.error('{}'.format(proc.stderr.decode('utf8')))
          self.destroy_container()
          self.destroy_network()
          sys.exit(1)
      logger.info('Network {} Created'.format(network))

    for node,cmds in self.create_node_cmd.items():
      logger.info('{} commands Executing...'.format(node))
      for cmd in cmds:
        proc = subprocess.run(cmd,stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        if proc.returncode == 0:
          logger.info('command: {}'.format(cmd))
        else:
          logger.error('{}: {}'.format(node,cmd))
          logger.error('{}'.format(proc.stderr.decode('utf8')))
          self.destroy_container()
          self.destroy_network()
          sys.exit(1)
      logger.info('{} commands Executed'.format(node))

    return logger.info('Network create commands Executed')

  def destroy_network(self):
    logger.info('Network destroy commands Executing...')

    #for network,cmds in self.destroy_cmd.items():
    #  logger.info('Network {} Destroing...'.format(network))
    #  for cmd in cmds:
    #    proc = subprocess.run(cmd,stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    #    if proc.returncode == 0:
    #      logger.info('command: {}'.format(cmd))
    #    else:
    #      logger.error('{}: {}'.format(network,cmd))
    #      logger.error('{}'.format(proc.stderr.decode('utf8')))
    #      sys.exit(1)
    #  logger.info('Network {} Destroyed'.format(network))
      
    proc = subprocess.run("ip netns | awk '{ print $1 }'",stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    if proc.returncode == 0:
      namespaces = proc.stdout.decode('utf8').split()
    else:
      logger.error('{}'.format(proc.stderr.decode('utf8')))
      sys.exit(1)
    for namespace in namespaces:
      if self.prefix in namespace:
        cmd = 'ip netns del {}'.format(namespace)
        proc = subprocess.run(cmd,stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        if proc.returncode == 0:
          logger.info('command: {}'.format(cmd))
        else:
          logger.error('{}'.format(proc.stderr.decode('utf8')))
          sys.exit(1)
    
    return logger.info('Network destroy commands Executed')

nsnet = Nsnet()

def command_create(args):
  logger.info('Command create Starting...')
  logger.info('')
  nsnet.create_container()
  nsnet.create_network()
  logger.info('Command create Completed')

def command_destroy(args):
  logger.info('Command destroy Starting...')
  logger.info('')
  nsnet.destroy_container()
  nsnet.destroy_network()
  logger.info('Command destroy Completed')

def command_recreate(args):
  logger.info('Command recreate Starting...')
  logger.info('')
  nsnet.destroy_container()
  nsnet.destroy_network()
  nsnet.create_container()
  nsnet.create_network()
  logger.info('Command recreate Completed')

def command_shell(args):
  proc = subprocess.Popen('docker-compose exec {} bash'.format(args.service), shell=True)
  proc.wait()

def main():
  if not (os.geteuid() == 0 and os.getuid() == 0) :
    print('This program must be run as root')
    sys.exit(1)

  parser = argparse.ArgumentParser(prog='nsnet',description='Nsnet creat docker container with flexible network')
  subparsers = parser.add_subparsers(dest='command')
  subparsers.required = True

  subparsers_option = argparse.ArgumentParser(add_help=False)
  subparsers_option.add_argument('-cf', '--composefile', default='docker-compose.yml', help='docker compose yaml file on the same directory')

  parser_create = subparsers.add_parser('create',help='Create and start nsnet', parents = [subparsers_option])
  parser_create.add_argument('-nf', '--netfile', default='net.yaml', help='network yaml file on the same directory')
  parser_create.set_defaults(func=command_create)

  parser_recreate = subparsers.add_parser('recreate',help='Recreate and restart nsnet', parents = [subparsers_option])
  parser_recreate.add_argument('-nf', '--netfile', default='net.yaml', help='network yaml file on the same directory')
  parser_recreate.set_defaults(func=command_recreate)

  parser_destroy = subparsers.add_parser('destroy',help='Stop and remove nsnet', parents = [subparsers_option])
  parser_destroy.set_defaults(func=command_destroy)

  parser_shell = subparsers.add_parser('shell',help='Shell connect container', parents = [subparsers_option])
  parser_shell.add_argument('service', help='container-name on docker-compose.yml')
  parser_shell.set_defaults(func=command_shell)

  args = parser.parse_args()
  
  nsnet.prefix = os.path.basename(os.getcwd())
  nsnet.composefile = args.composefile
  if not os.path.exists(nsnet.composefile):
    logger.error('{} not found in current directory'.format(nsnet.composefile))
    sys.exit(1)

  if args.command in ['create','recreate']:
    nsnet.netfile = args.netfile
    try:
      nsnet.load_netfile()
      nsnet.read_netfile()
    except Exception as e:
      logger.error('Exception occurred while loading network yaml file ...')
      logger.error(e)
      sys.exit(1)
  
  args.func(args)