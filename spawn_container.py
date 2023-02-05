#!python3
# prerequesites "pip install pyyaml docker" and a running docker instance with permissions to build / deploy images and run instances
import yaml
import docker
import os
import logging
from logging import warning, info, debug, error, INFO
import sys
from time import sleep

logging.basicConfig(level=INFO, format='%(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
logging.getLogger().addHandler(logging.FileHandler(filename='containers.log'))

#client = docker.from_env()
client = docker.DockerClient(base_url='unix://var/run/docker.sock')
# build the image with build.sh in docker dir
imagename = "vexsl/queue-specialist:1.0"

pwd = os.getcwd()

with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.Loader)

start_port = data["location"][data["current_site"]]["start_port"]
for user in data["users"]:
    if user["login_location"] == data['current_site']:
        if "multi_login" in user:
            if isinstance(user["multi_login"], int):
                no_instances = user["multi_login"]
                info(f"multiple ({no_instances}) logins for user {user['username']}")
        else:
            no_instances = 1

        for n in range(no_instances):
            env_list = [f'TML_USER={user["username"]}', f'TML_PASS={user["password"]}', 'VNC_RESOLUTION=1920x1080', f'MY_PORT={start_port}', f'MY_HOST={data["current_site"]}', f'MY_IP={data["location"][data["current_site"]]["ip"]}', 'VNC_PASSWORDLESS=true']
            info(f"starting container with env list {env_list}")
            client.containers.run(imagename, detach=True, auto_remove=True, name=f'queue{start_port}',
                                  ports={'6901/tcp': start_port}, volumes={pwd: {'bind': '/headless/queue', 'mode': 'rw'}},
                                  environment=env_list)
            info(f"running exec on container queue{start_port}")
            sleep(2)
            client.containers.get(f'queue{start_port}').exec_run("/usr/bin/xfce4-terminal -e \"/bin/bash -c '/usr/bin/python3 /headless/queue/queue_holder.py;bash'\"", detach=True)
            start_port += 1

info(f"stop containers with \t\t docker stop $(docker ps -a -q --filter ancestor={imagename} --format=\"{{{{.ID}}}}\")")
