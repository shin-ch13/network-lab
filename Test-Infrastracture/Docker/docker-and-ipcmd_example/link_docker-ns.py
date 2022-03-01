#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import json

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

  def get_container_id(self,container_service):
    proc = subprocess.run(['docker-compose','ps',container_service,'--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      json_dict = json.loads(proc.stdout.decode('utf8'))
      container_id= json_dict[0]['ID']
    else:
      print('{}'.format(proc.stderr.decode('utf8')))
      sys.exit(1)
    return container_id

  def get_container_pid(self,container_id):
    proc = subprocess.run(['docker','inspect',container_id,'--format','{{.State.Pid}}'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      container_pid = proc.stdout.decode('utf8').strip()
      if os.path.isfile('/proc/{}/ns/net'.format(container_pid)):
        container_pid_path = '/proc/{}/ns/net'.format(container_pid)
      else:
        print('/proc/{}/ns/net file not found'.format(container_pid))
        sys.exit(1)
    else:
      print('{}'.format(proc.stderr.decode('utf8')))
      sys.exit(1)
    return container_pid,container_pid_path

def get_docker_infos(services):
  container_infos = []
  '''
  {
    {
      'container_service': 'node1'
      'container_name': 'docker-node1-1'
      'container_id': 111111111111111
      'container_pid': 1111
      'container_pid_path':
    }
    ...
  }
  '''
  dockercmd = DockerCommand()
  dockercmd.check_compose_file()
  for container_service in dockercmd.get_container_service(services):
    container_name = dockercmd.get_container_name(container_service)
    container_id = dockercmd.get_container_id(container_service)
    container_pid, container_pid_path = dockercmd.get_container_pid(container_id)
    container_infos.append({
      'container_service':container_service,
      'container_name':container_name,
      'container_id':container_id,
      'container_pid':container_pid,
      'container_pid_path':container_pid_path
    })
  print(container_infos)
  return container_infos

def link_show(args):
  container_infos = get_docker_infos(args.container)
  if os.path.exists('/var/run/netns'):
    for i in range(len(container_infos)):
      if os.path.lexists('/var/run/netns/{}'.format(container_infos[i]['container_service'])):
        if os.path.islink('/var/run/netns/{}'.format(container_infos[i]['container_service'])):
          print('{}: /var/run/netns/{} -> {}'.format(
            container_infos[i]['container_service'],
            container_infos[i]['container_service'],
            os.readlink('/var/run/netns/{}'.format(container_infos[i]['container_service']))
          ))
        else:
          print('{}: /var/run/netns/{} symbolic link not found'.format(
            container_infos[i]['container_service'],
            container_infos[i]['container_service']
          ))
      else:
        print('{}: /var/run/netns/{} file not found'.format(
          container_infos[i]['container_service'],
          container_infos[i]['container_service']
        ))
  else:
    print('/var/run/netns directory not found')

def link_show_force(args):
  if os.path.exists('/var/run/netns'):
    for i in range(len(args.container)):
      if os.path.lexists('/var/run/netns/{}'.format(args.container[i])):
        if os.path.islink('/var/run/netns/{}'.format(args.container[i])):
          print('{}: /var/run/netns/{} -> {}'.format(
            args.container[i],
            args.container[i],
            os.readlink('/var/run/netns/{}'.format(args.container[i]))
          ))
        else:
          print('{}: /var/run/netns/{} symbolic link not found'.format(
            args.container[i],
            args.container[i]
          ))
      else:
        print('{}: /var/run/netns/{} file not found'.format(
          args.container[i],
          args.container[i]
        ))
  else:
    print('/var/run/netns directory not found')
    
def link_on(args):
  container_infos = get_docker_infos(args.container)
  if not os.path.exists('/var/run/netns'):
    os.mkdir('/var/run/netns')
  for i in range(len(container_infos)):
    if os.path.lexists('/var/run/netns/{}'.format(container_infos[i]['container_service'])):
      if os.path.islink('/var/run/netns/{}'.format(container_infos[i]['container_service'])):
        print('{}: /var/run/netns/{} -> {} symbolic link already exist'.format(
          container_infos[i]['container_service'],
          container_infos[i]['container_service'],
          os.readlink('/var/run/netns/{}'.format(container_infos[i]['container_service']))
        ))
      else:
        os.symlink(
          container_infos[i]['container_pid_path'],
          '/var/run/netns/{}'.format(container_infos[i]['container_service'])
        )
        print('{}: /var/run/netns/{} -> {} symbolic link create'.format(
          container_infos[i]['container_service'],
          container_infos[i]['container_service'],
          os.readlink('/var/run/netns/{}'.format(container_infos[i]['container_service']))
        ))
    else:
      os.symlink(
          container_infos[i]['container_pid_path'],
          '/var/run/netns/{}'.format(container_infos[i]['container_service'])
      )
      print('{}: /var/run/netns/{} -> {} symbolic link create'.format(
        container_infos[i]['container_service'],
        container_infos[i]['container_service'],
        os.readlink('/var/run/netns/{}'.format(container_infos[i]['container_service']))
      ))

def link_off(args):
  container_infos = get_docker_infos(args.container)
  for i in range(len(container_infos)):
    if os.path.lexists('/var/run/netns/{}'.format(container_infos[i]['container_service'])):
      print('{}: /var/run/netns/{} -> {} symbolic link destroy'.format(
        container_infos[i]['container_service'],
        container_infos[i]['container_service'],
        os.readlink('/var/run/netns/{}'.format(container_infos[i]['container_service']))
      ))
      os.unlink(
        '/var/run/netns/{}'.format(container_infos[i]['container_service'])
      )
    else:
      print('{}: /var/run/netns/{} file not found'.format(
        container_infos[i]['container_service'],
        container_infos[i]['container_service']
      ))

def link_off_force(args):
  for i in range(len(args.container)):
    if os.path.lexists('/var/run/netns/{}'.format(args.container[i])):
      print('{}: /var/run/netns/{} -> {} symbolic link destroy'.format(
        args.container[i],
        args.container[i],
        os.readlink('/var/run/netns/{}'.format(args.container[i]))
      ))
      os.unlink(
        '/var/run/netns/{}'.format(args.container[i])
      )
    else:
      print('{}: /var/run/netns/{} file not found'.format(
        args.container[i],
        args.container[i]
      ))

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

  parser_link_show_force = subparsers.add_parser('link-show-force',help='Forcibly Link Show docker-namespace-id')
  parser_link_show_force.set_defaults(func=link_show_force)
  parser_link_show_force.add_argument('-c', '-C', '--container', nargs='*', required=True, help='container-name on docker-compose.yml')

  parser_link_on = subparsers.add_parser('link-on',help='Link On docker-namespace-id to host-namespace')
  parser_link_on.set_defaults(func=link_on)
  parser_link_on.add_argument('-c', '-C', '--container', nargs='*', default='ALL', help='container-name on docker-compose.yml (default:ALL)')

  parser_link_off = subparsers.add_parser('link-off',help='Link Off docker-namespace-id to host-namespace')
  parser_link_off.set_defaults(func=link_off)
  parser_link_off.add_argument('-c', '-C', '--container', nargs='*', default='ALL', help='container-name on docker-compose.yml (default:ALL)')

  parser_link_off_force = subparsers.add_parser('link-off-force',help='Forcibly Link Off docker-namespace-id to host-namespace')
  parser_link_off_force.set_defaults(func=link_off_force)
  parser_link_off_force.add_argument('-c', '-C', '--container', nargs='*', required=True, help='container-name on docker-compose.yml')

  #parser.print_help()

  args = parser.parse_args()
  args.func(args)

main()