#!/usr/bin/env python3
import sys
import os
import argparse
from dockercmd_module import DockerCommand

def get_docker_infos(services):
  container_infos = []
  '''
  {
    {
      'container_service': 'node1'
      'container_name': 'docker-node1-1'
      'container_id': '111111aaaaaaaaa'
      'container_pid': '1111'
      'container_pid_path': '/proc/1111/ns/net'
    }
    ...
  }
  '''
  dockercmd = DockerCommand()
  for container_service in dockercmd.get_container_service(services):
    container_name = dockercmd.get_container_name(container_service)
    container_id = dockercmd.get_container_id(container_name)
    container_pid, container_pid_path = dockercmd.get_container_pid(container_id)
    container_infos.append({
      'container_service':container_service,
      'container_name':container_name,
      'container_id':container_id,
      'container_pid':container_pid,
      'container_pid_path':container_pid_path
    })
  return container_infos

def link_show(args):
  dockercmd = DockerCommand()
  container_services = dockercmd.get_container_service(args.container)
  if os.path.exists('/var/run/netns'):
    for container_service in container_services:
      if os.path.lexists('/var/run/netns/{}'.format(container_service)):
        if os.path.islink('/var/run/netns/{}'.format(container_service)):
          print('{}: /var/run/netns/{} -> {}'.format(
            container_service,
            container_service,
            os.readlink('/var/run/netns/{}'.format(container_service))
          ))
        else:
          print('{}: /var/run/netns/{} symbolic link not found'.format(
            container_service,
            container_service
          ))
      else:
        print('{}: /var/run/netns/{} file not found'.format(
          container_service,
          container_service
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
  dockercmd = DockerCommand()
  container_services = dockercmd.get_container_service(args.container)
  for container_service in container_services:
    if os.path.lexists('/var/run/netns/{}'.format(container_service)):
      print('{}: /var/run/netns/{} -> {} symbolic link unlink'.format(
        container_service,
        container_service,
        os.readlink('/var/run/netns/{}'.format(container_service))
      ))
      os.unlink(
        '/var/run/netns/{}'.format(container_service)
      )
    else:
      print('{}: /var/run/netns/{} file not found'.format(
        container_service,
        container_service
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