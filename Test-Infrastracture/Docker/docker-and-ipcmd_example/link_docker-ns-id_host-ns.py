#!/usr/bin/env python3
import argparse
import subprocess
import json
import pprint

class DockerCommand:
  def get_container_name(self,args):
    if 'ALL' in args.container:
      #print('ALL')
      proc = subprocess.run(['docker-compose','ps','--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      #print(proc.stdout.decode('utf8'))
      json_dict = json.loads(proc.stdout.decode('utf8'))
      if not json_dict:
        print('docker process not up')
      else:
        for i in range(len(json_dict)):
          print(json_dict[i]['ID'])
    else:
      for container in args.container:
        #print(container)
        proc = subprocess.run(['docker-compose','ps',container,'--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        #print(proc.stdout.decode("utf8"))
        if proc.returncode == 0:
          json_dict = json.loads(proc.stdout.decode('utf8'))
          print(json_dict[0]['ID'])
        else:
          print('{}'.format(proc.stderr.decode('utf8')))


def link_show(args):
#  print(args.command)
  print(args.container)

def link_on(args):
  print(args.container)

def link_off(args):
  print(args.container)

def main():
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
  dockercmd = DockerCommand()
  dockercmd.get_container_name(args)

  args.func(args)

main()