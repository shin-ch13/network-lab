#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import json
import pprint

class DockerCommand:
  def check_compose_file(self):
    path = 'docker-compose.yml'
    is_file = os.path.isfile(path)
    if not is_file:
      print(f"{path} not found in current directory")
      sys.exit(1)

  def get_container_service(self,services):
    container_services = []
    if 'ALL' in services:
      proc = subprocess.run(['docker-compose','ps','--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      json_dict = json.loads(proc.stdout.decode('utf8'))
      if not json_dict:
        print('docker container not up')
        sys.exit(1)
      else:
        for i in range(len(json_dict)):
          container_service = json_dict[i]['Service']
          container_services.append(container_service)
    else:
      for service in services:
        proc = subprocess.run(['docker-compose','ps',service,'--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        if proc.returncode == 0:
          json_dict = json.loads(proc.stdout.decode('utf8'))
          container_service = json_dict[0]['Service']
          container_services.append(container_service)
        else:
          print('{}'.format(proc.stderr.decode('utf8')))
          sys.exit(1)
    return container_services

  def get_container_name(self,container_service):
    proc = subprocess.run(['docker-compose','ps',container_service,'--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      json_dict = json.loads(proc.stdout.decode('utf8'))
      container_name = json_dict[0]['Name']
    else:
      print('{}'.format(proc.stderr.decode('utf8')))
      sys.exit(1)
    return container_name

  def get_container_pid(self,container_service):
    proc = subprocess.run(['docker-compose','ps',container_service,'--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      json_dict = json.loads(proc.stdout.decode('utf8'))
      proc = subprocess.run(['docker','inspect',json_dict[0]['ID'],'--format','\'{{.State.Pid}}\''],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      if proc.returncode == 0:
        container_pid = proc.stdout.decode('utf8').replace('\n','').replace('\'','')
      else:
        print('{}'.format(proc.stderr.decode('utf8')))
        sys.exit(1)
    else:
      print('{}'.format(proc.stderr.decode('utf8')))
      sys.exit(1)
    return container_pid

def get_docker_infos(services):
  docker_infos[]
  '''
  {
    {
      'container_service': 'node1'
      'container_name': 'docker-node1-1'
      'container_pid': 1111
      'container_pid_path':

  }
  '''

  dockercmd = DockerCommand()
  dockercmd.check_compose_file()
  print(dockercmd.get_container_service(services))
  for container_service in dockercmd.get_container_service(services):
    container_name = dockercmd.get_container_name(container_service)
    container_pid = dockercmd.get_container_pid(container_service)
    if os.path.isfile('/proc/{}/ns/net'.format(container_pid)):
      container_pid_path = '/proc/{}/ns/net'.format(conatiner_pid)
    else:
      print('/proc/{}/ns/net not found'.format(container_pid))
      sys.exit(1)


def link_show(args):
  get_docker_infos(args.container)
  print(container_pids)
  for container_pid in container_pids:
    if os.path.isfile('/proc/{}/ns/net'.format(container_pid)):
      if os.path.islink('/proc/{}/ns/net'.format(container_pid)):
        print(os.readlink('/proc/{}/ns/net'.format(container_pid)))
      else:
        print('/proc/{}/ns/net symbolic link not found'.format(container_pid))
    else:
      print('/proc/{}/ns/net not found'.format(container_pid))

def link_on(args):
  print(pids)

def link_off(args):
  print(pids)

def main():
  if not (os.geteuid() == 0 and os.getuid() == 0) :
    print('This program must be run as root')
    sys.exit(1)

  parser = argparse.ArgumentParser(prog='link_docker-ns-id_host-ns',description='This program links dokcer-namespace-id to host-namespace')

  subparsers = parser.add_subparsers(dest='command')
  subparsers.required = True

  parser_link_show = subparsers.add_parser('link-show',help='Link Show docker-namespace-id')
  parser_link_show.set_defaults(func=link_show)
  parser_link_show.add_argument('-c', '-C', '--container', nargs='*', default='ALL', help='container-name on docker-compose.yml (default:ALL)')

  parser_link_on = subparsers.add_parser('link-on',help='Link On docker-namespace-id to host-namespace')
  parser_link_on.set_defaults(func=link_on)
  parser_link_on.add_argument('-c', '-C', '--container', nargs='*', default='ALL', help='container-name on docker-compose.yml (default:ALL)')

  parser_link_off = subparsers.add_parser('link-off',help='Link Off docker-namespace-id to host-namespace')
  parser_link_off.set_defaults(func=link_off)
  parser_link_off.add_argument('-c', '-C', '--container', nargs='*', default='ALL', help='container-name on docker-compose.yml (default:ALL)')

  #parser.print_help()

  args = parser.parse_args()
  args.func(args)

main()