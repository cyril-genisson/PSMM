#!/usr/bin/env python3
from ssh_login import SSHConnection
from ssh_mariadb import MariaDBSSHConnector
import os
import json

def str2dict(string):
    return eval(string)


def main(srv):
    with open(srv) as f:
        services = json.load(f)
    user=os.getenv("USER")
    for key, data in services.items():
        connection = SSHConnection(hostname=data["host"], username=user, use_ssh_agent=True)
        connection.connect()
        com, out, err = connection.exec_command(command=data["journal"])
        connection.close()
        w = out.split('\n')
        w.pop()
        for k in w:
            for key, data in eval(k).items():
                if key == "MESSAGE":
                    print(data)


if __name__ == '__main__':
    main("services.json")