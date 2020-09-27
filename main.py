from flask import *
import paramiko
import re
from config import Config

app = Flask(__name__)


def remove_mulitple_space(s):
    return re.sub('  +', ',', s)


def process_docker_names(res):
    groups = {}
    res.pop(0)
    for docker_container in res:
        p_str = remove_mulitple_space(docker_container).split(",")
        prefix, remainder = p_str[5].split('_', 1)
        groups.setdefault(prefix, []).append(remainder)
    return groups


def li(host, cmd, username, password, port):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)

    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()

    outlines = stdout.readlines()
    res = "".join(outlines)
    resp = [x.strip() for x in filter(None, res.split('\n'))]
    return resp


@app.route('/')
def home():
    return {
        "message": "Docker API is running",
    }


@app.route('/dc_list',methods = ['GET'])
def dc_list():
    li_output = {}
    rs = {}

    host = Config.HOST
    username = Config.USERNAME
    port=Config.PORT
    password = Config.PASSWORD
    error = ["Not able to connect to the server"]
    cmd = "sudo -S docker ps"

    try:
        li_output[host] = li(host, cmd, username, password,port)
    except:
        li_output[host] = error

    rs[host] = process_docker_names(li_output[host])
    return rs

@app.route('/dc_create',methods = ['POST'])
def dc_create():
    li_output = {}
    return li_output


if __name__ == '__main__':
   app.run(debug = True)