#!/usr/bin/env python3
import sys
import os
import argparse
from dockercmd_module import DockerCommand

def link_show(service):
  dockercmd = DockerCommand()
  container_services = dockercmd.get_container_service(service)
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
    
def link_on(service):
  dockercmd = DockerCommand()
  container_infos = dockercmd.get_container_infos(service)
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

def link_off(service):
  dockercmd = DockerCommand()
  container_services = dockercmd.get_container_service(service)
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

def link_show(service):
  dockercmd = DockerCommand()
  container_services = dockercmd.get_container_service(service)
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
    
def command_link_show(args):
  link_show(args.service)

def command_link_on(args):
  link_on(args.service)

def command_link_off(args):
  link_off(args.service)

def main():
  if not (os.geteuid() == 0 and os.getuid() == 0) :
    sys.stderr.write('This program must be run as root')
    sys.exit(1)

  parser = argparse.ArgumentParser(prog='link_docker-ns-id_host-ns',description='This program links dokcer-namespace-id to host-namespace')
  subparsers = parser.add_subparsers(dest='command')
  subparsers.required = True

  subparsers_option = argparse.ArgumentParser(add_help=False)
  subparsers_option.add_argument('service', nargs='*', default='ALL', help='container-name on docker-compose.yml (default:ALL)')

  parser_link_show = subparsers.add_parser('link-show',help='Link Show docker-namespace-id', parents = [subparsers_option])
  parser_link_show.set_defaults(func=command_link_show)

  parser_link_on = subparsers.add_parser('link-on',help='Link On docker-namespace-id to host-namespace', parents = [subparsers_option])
  parser_link_on.set_defaults(func=command_link_on)

  parser_link_off = subparsers.add_parser('link-off',help='Link Off docker-namespace-id to host-namespace', parents = [subparsers_option])
  parser_link_off.set_defaults(func=command_link_off)


  #parser.print_help()

  args = parser.parse_args()
  args.func(args)