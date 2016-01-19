#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, abort
from flask.ext.basicauth import BasicAuth
from flask.ext.mysql import MySQL
from paramiko.client import SSHClient
from paramiko import AutoAddPolicy


app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'crc-user'
app.config['BASIC_AUTH_PASSWORD'] = 'crc-pass'
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

#mysql = MySQL()
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
#app.config['MYSQL_DATABASE_DB'] = 'crc-server'
#app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
#mysql.init_app(app)

@app.errorhandler(404)
def resource_not_found(e):
    response = {'message': 'Resource Not Found'}
    response = jsonify(response)
    response.status_code = 404
    return response

@app.errorhandler(401)
def not_authorized(e):
    response = {'message': 'Not Authorized'}
    response = jsonify(response)
    response.status_code = 401
    return response

@app.errorhandler(400)
def not_authorized(e):
    response = {'message': 'Bad Request'}
    response = jsonify(response)
    response.status_code = 400
    return response

@app.errorhandler(405)
def not_authorized(e):
    response = {'message': 'Method Not Allowed'}
    response = jsonify(response)
    response.status_code = 405
    return response



@app.route('/api/v1/vm/<vm_name>/status', methods=['GET'])
def api_vm_status(vm_name):
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        abort(400)
    else:
        try:
            if vm_name[-1:] == 'w':
                vm_internal_name = ''
            elif vm_name[-1:] == 'u':
                vm_internal_name = ''
            else:
                vm_internal_name = ''

            client = nodes[vm_name[:-1]]['ssh']
            stdin, stdout, stderr = client.exec_command(
                'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

            if len(stdout) == 0:
                return abort(400)

            stdin, stdout, stderr = client.exec_command(
                'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

            if len(stdout) == 0:
                jsonify({'status': 'off'})
            else:
                jsonify({'status': 'on'})

        except:
            abort(500)


def vm_start(node_name, vm_name):
    global nodes  

    if vm_name == 'w':
        vm_internal_name = ''
    elif vm_name == 'u':
        vm_internal_name = ''
    else:
        vm_internal_name = ''

    client = nodes[node_name]['ssh']

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout) == 0:
        return abort(400)

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout) == 0:
        client.exec_command('VBoxManage startvm {0}'.format(vm_internal_name)) 


@app.route('/api/v1/vm/<vm_name>/start', methods=['POST'])
def api_vm_start(vm_name):        
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        abort(400)
    else:
        thread = threading.Thread(
            target=vm_start, 
            rgs=(vm_name[:-1], vm_name[-1:]))
        thread.start()        


def vm_stop(node_name, vm_name):
    global nodes   

    if vm_name == 'w':
        vm_internal_name = ''
    elif vm_name == 'u':
        vm_internal_name = ''
    else:
        vm_internal_name = ''

    client = nodes[node_name]['ssh']

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout) == 0:
        return abort(400)

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout) > 0:
        client.exec_command('VBoxManage controlvm {0} poweroff soft'.format(vm_internal_name)) 


@app.route('/api/v1/vm/<vm_name>/stop', methods=['POST'])
def api_vm_stop(vm_name):        
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        abort(400)
    else:
        thread = threading.Thread(
            target=vm_stop, 
            rgs=(vm_name[:-1], vm_name[-1:]))
        thread.start() 

def vm_reset(node_name, vm_name):
    global nodes   

    if vm_name == 'w':
        vm_internal_name = ''
    elif vm_name == 'u':
        vm_internal_name = ''
    else:
        vm_internal_name = ''

    client = nodes[node_name]['ssh']

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout) == 0:
        return abort(400)

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout) == 0:
        client.exec_command('VBoxManage startvm {0}'.format(vm_internal_name)) 
    else:
        client.exec_command('VBoxManage controlvm {0} reset'.format(vm_internal_name))


@app.route('/api/v1/vm/<vm_name>/reset', methods=['POST'])
def api_vm_reset(vm_name):        
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        abort(400)
    else:
        thread = threading.Thread(
            target=vm_reset, 
            rgs=(vm_name[:-1], vm_name[-1:]))        
        thread.start() 


@app.route('/api/v1/image/load', methods=['POST'])
def api_image_load():        
    abort(400)

@app.route('/api/v1/image/load/<task_id>', methods=['GET'])
def api_image_load_status(task_id):        
    abort(400)

@app.route('/api/v1/image/save', methods=['POST'])
def api_image_save():        
    abort(400)

@app.route('/api/v1/image/save/<task_id>', methods=['GET'])
def api_image_save_status(task_id):        
    abort(400)



@app.route('/api/v1/user/', methods=['POST'])
def api_user_create():        
    abort(400)

@app.route('/api/v1/user/<username>', methods=['DELETE'])
def api_user_delete(username):
    abort(400)



@app.route('/api/v1/slice/', methods=['POST'])
def api_slice_create():        
    abort(400)



@app.route('/api/v1/experiment/', methods=['POST'])
def api_experiment_execute():        
    abort(400)

@app.route('/api/v1/experiment/<exp_id>', methods=['GET'])
def api_experiment_status(exp_id):        
    abort(400)


def start_ssh_pool():
    global nodes

    try:
        with open("/etc/dnsmasq.d/testbed.conf") as config_file:
            parse_node = False
            for line in config_file:                
                if parse_node:
                    node_params = line.strip().rstrip().split(',')
                    nodes[node_params[2]] = {
                        'mac':  node_params[1],
                        'ip':   node_params[3]
                    }
                    parse_node = False
                elif line.startswith('#NODE'):
                    parse_node = True
    except Exception, err:
        print 'Error parsing nodes config file'
        print err      
        exit(1)

    try:
        for k,v in nodes.iteritems():
            print 'Setting up a connection with {0}'.format(k)
            print 'Connecting to {0}'.format(v['ip'])

            client = SSHClient()            
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(v['ip'], username='node5', password='crc123')

            nodes[k]['ssh'] = client

    except Exception, err:
        print 'Error establishing ssh connection to nodes' 
        print err          
        exit(1)

nodes = {}

if __name__ == '__main__':

    start_ssh_pool()
    
    app.run(
        host='0.0.0.0', 
        port=7777,
        debug=False,
        threaded=True) 

    for k,v in nodes.iteritems():
        print 'Closing connection {0}'.format(k)
        v['ssh'].close
