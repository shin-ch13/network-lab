#!/usr/bin/env python3
import sys
import os
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
    self.check_compose_file()
    container_services = []
    if 'ALL' in services:
      proc = subprocess.run(['docker-compose','config','--services'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      if proc.returncode == 0:
        container_services = proc.stdout.decode('utf8').split()
      else:
        print('{}'.format(proc.stderr.decode('utf8')))
        sys.exit(1)
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
    self.check_compose_file()
    proc = subprocess.run(['docker-compose','ps',container_service,'--format=json'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      json_dict = json.loads(proc.stdout.decode('utf8'))
      container_name = json_dict[0]['Name']
    else:
      print('{}'.format(proc.stderr.decode('utf8')))
      sys.exit(1)
    return container_name

  def get_container_id(self,container_name):
    proc = subprocess.run(['docker','inspect',container_name,'--format','{{.Id}}'],stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc.returncode == 0:
      container_id= proc.stdout.decode('utf8').strip()
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