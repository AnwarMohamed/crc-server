#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, abort, request
from flask.ext.basicauth import BasicAuth
from flask.ext.mysql import MySQL
from paramiko.client import SSHClient
from paramiko import AutoAddPolicy
from subprocess import call
import threading, os, random, string, portalocker

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'crc-user'
app.config['BASIC_AUTH_PASSWORD'] = 'crc-pass'
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'CRC123'
app.config['MYSQL_DATABASE_DB'] = 'crc-testbed'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

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

vms_mapping = {
    'w': 'vm1',
    'u': 'vm2',
    'r': 'vm3'
}

@app.route('/api/v1/vm/<vm_name>/status', methods=['GET'])
def api_vm_status(vm_name):
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        abort(400)
    else:
        try:            
            vm_internal_name = vms_mapping[vm_name[-1:]]

            client = nodes[vm_name[:-1]]['ssh']
            stdin, stdout, stderr = client.exec_command(
                'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))                
            if len(stdout.read()) == 0:
                return abort(400)

            stdin, stdout, stderr = client.exec_command(
                'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

            if len(stdout.read()) == 0:
                return jsonify({'status': 'off'})
            else:
                return jsonify({'status': 'on'})

        except Exception, err:
            print err
            abort(500)


def vm_start(node_name, vm_name):
    global nodes  

    vm_internal_name = vms_mapping[vm_name]

    client = nodes[node_name]['ssh']

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        return None

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        client.exec_command('VBoxManage startvm {0} --type headless'.format(vm_internal_name)) 


@app.route('/api/v1/vm/<vm_name>/start', methods=['POST'])
def api_vm_start(vm_name):        
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        return abort(400)
    else:
        thread = threading.Thread(
            target=vm_start, 
            args=(vm_name[:-1], vm_name[-1:]))
        thread.start()

    return ''


def vm_stop(node_name, vm_name):
    global nodes   

    vm_internal_name = vms_mapping[vm_name]

    client = nodes[node_name]['ssh']

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        return None

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) > 0:
        client.exec_command('VBoxManage controlvm {0} poweroff soft'.format(vm_internal_name)) 


@app.route('/api/v1/vm/<vm_name>/stop', methods=['POST'])
def api_vm_stop(vm_name):        
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        abort(400)
    else:
        thread = threading.Thread(
            target=vm_stop, 
            args=(vm_name[:-1], vm_name[-1:]))
        thread.start() 

    return ''      


def vm_reset(node_name, vm_name):
    global nodes   

    vm_internal_name = vms_mapping[vm_name]

    client = nodes[node_name]['ssh']

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        return None

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        client.exec_command('VBoxManage startvm {0} --type headless'.format(vm_internal_name)) 
    else:
        client.exec_command('VBoxManage controlvm {0} reset'.format(vm_internal_name))


@app.route('/api/v1/vm/<vm_name>/reset', methods=['POST'])
def api_vm_reset(vm_name):        
    global nodes
    if vm_name[:-1] not in nodes or vm_name[-1:] not in 'wur':
        return abort(400)
    else:
        thread = threading.Thread(
            target=vm_reset, 
            args=(vm_name[:-1], vm_name[-1:]))        
        thread.start() 

    return ''


def image_load(name, path, node_list, task_id):    
    call(["mkdir", "-p", "tasks/"])
    call(["touch", "tasks/{0}-load.lock".format(task_id)])
    call(["./omf_load.sh", "{0}".format(','.join(node_list)), "{0}".format(name), "{0}".format(task_id)])
    call(["rm", "tasks/{0}-load.lock".format(task_id)])

@app.route('/api/v1/image/load', methods=['POST'])
def api_image_load():

    json_req = request.get_json(force=True, silent=True)
    json_params = ['name', 'path', 'nodes_list']

    if json_req == None or any(param not in json_req for param in json_params):            
        return abort(400)

    if os.path.exists(json_req['path']) == False:
        return abort(400)

    task_id = ''.join(random.SystemRandom()
        .choice(string.ascii_uppercase + string.digits) for _ in range(12))

    thread = threading.Thread(
        target=image_load, 
        args=(json_req['name'], json_req['path'], json_req['nodes_list'], task_id))
    thread.start()

    return jsonify({'task_id': task_id})

@app.route('/api/v1/image/load/<task_id>', methods=['GET'])
def api_image_load_status(task_id):        

    progress_log = "tasks/{0}-load.progress".format(task_id)
    error_log = "tasks/{0}-load.error".format(task_id)    
    
    if os.path.exists(progress_log) == False:
        return abort(400)

    progress = 'Not Started'
    with open(progress_log, 'r') as plog:
        for line in plog:
            pass
        progress = line

    return jsonify({
        'task_id': task_id,
        'progress': progress,
        'error': os.path.exists(error_log)
    })


def image_save(name, path, node_list, task_id):    
    call(["mkdir", "-p", "tasks/"])
    call(["touch", "tasks/{0}-save.lock".format(task_id)])
    call(["./omf_save.sh", "{0}".format(','.join(node_list)), "{0}".format(name), "{0}".format(task_id)])
    call(["rm", "tasks/{0}-save.lock".format(task_id)])

@app.route('/api/v1/image/save', methods=['POST'])
def api_image_save():        

    json_req = request.get_json(force=True, silent=True)
    json_params = ['name', 'path', 'nodes_list']

    if json_req == None or any(param not in json_req for param in json_params):            
        return abort(400)

    if os.path.exists(json_req['path']) == False:
        return abort(400)

    task_id = ''.join(random.SystemRandom()
        .choice(string.ascii_uppercase + string.digits) for _ in range(12))

    thread = threading.Thread(
        target=image_save, 
        args=(json_req['name'], json_req['path'], json_req['nodes_list'], task_id))
    thread.start()

    return jsonify({'task_id': task_id})


@app.route('/api/v1/image/save/<task_id>', methods=['GET'])
def api_image_save_status(task_id):

    progress_log = "tasks/{0}-save.progress".format(task_id)
    error_log = "tasks/{0}-save.error".format(task_id)    
    
    if os.path.exists(progress_log) == False:
        return abort(400)

    progress = 'Not Started'
    with open(progress_log, 'r') as plog:
        for line in plog:
            pass
        progress = line

    return jsonify({
        'task_id': task_id,
        'progress': progress,
        'error': os.path.exists(error_log)
    })



@app.route('/api/v1/user/', methods=['POST'])
def api_user_create():        
    abort(400)

@app.route('/api/v1/user/<username>', methods=['DELETE'])
def api_user_delete(username):
    abort(400)



@app.route('/api/v1/slice/', methods=['POST'])
def api_slice_create():        
    
    json_req = request.get_json(force=True, silent=True)
    json_params = ['user_name', 'start_time', 'end_time']

    if json_req == None or any(param not in json_req for param in json_params):            
        return abort(400)

    conn = mysql.connect()
    cursor = conn.cursor()
    
    cursor.execute(
        "insert into slices values ('{0}','{1}','{2}') on duplicate key update start_time='{1}', end_time='{2}'"
        .format(json_req['user_name'], json_req['start_time'], json_req['end_time']))
    conn.commit()

    return ''


def experiment_execute(exp_id, path):    
    call(["mkdir", "-p", "experiments/{0}".format(exp_id)])
    call(["touch", "experiments/{0}/lock".format(exp_id)])

    log_file = open("experiments/{0}/log".format(exp_id), "w+")    

    call(["omf_ec", 
            "-u" ,"amqp://10.0.0.200", 
            "exec", 
            "--oml_uri", "tcp:10.0.0.200:3003", path], stdout=log_file)
    
    log_file.close()

    call(["rm", "experiments/{0}/lock".format(exp_id)])

@app.route('/api/v1/experiment/', methods=['POST'])
def api_experiment_execute(): 
    
    json_req = request.get_json(force=True, silent=True)

    if json_req == None or 'path' not in json_req:            
        return abort(400)

    if os.path.exists(json_req['path']) == False:
        return abort(400)

    exp_id = ''.join(random.SystemRandom()
        .choice(string.ascii_uppercase + string.digits) for _ in range(12))

    thread = threading.Thread(
        target=experiment_execute, 
        args=(exp_id, json_req['path']))        
    thread.start()

    return jsonify({'exp_id': exp_id})


@app.route('/api/v1/experiment/<exp_id>', methods=['GET'])
def api_experiment_status(exp_id):

    log_path = "experiments/{0}/log".format(exp_id)
    lock_path = "experiments/{0}/lock".format(exp_id)

    if os.path.exists(log_path) == False:
        return abort(400)

    try:
        log = []

        if os.path.exists(lock_path) == False:
            status = 'finished'
        else:
            status = 'running'

        with open("experiments/{0}/log".format(exp_id), 'r') as log_file:            
            for line in log_file:
                log.append(line.rstrip())

        return jsonify({'status': status, 'log': log})
    except:
        abort(400)


def start_ssh_pool():
    global nodes

    try:
        print ' * Parsing nodes config file'
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
        print ' x Error parsing nodes config file'
        print err      
        exit(1)
    finally:
        print

    try:
        for k,v in nodes.iteritems():
            print ' * Setting up a connection with {0}'.format(k)
            print ' * Connecting to {0}'.format(v['ip'])

            client = SSHClient()            
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(v['ip'], username='node5', password='crc123')

            nodes[k]['ssh'] = client

            print ' * Connected to {0} @ {1}\n'.format(k, v['ip'])

    except Exception, err:
        print ' x Error establishing ssh connection to nodes' 
        print err          
        exit(1)

nodes = {}

def start_logo():
    print '''
      __________  ______   ______          __  __             __
     / ____/ __ \/ ____/  /_  __/__  _____/ /_/ /_  ___  ____/ /
    / /   / /_/ / /        / / / _ \/ ___/ __/ __ \/ _ \/ __  / 
   / /___/ _, _/ /___     / / /  __(__  ) /_/ /_/ /  __/ /_/ /  
   \____/_/ |_|\____/    /_/  \___/____/\__/_.___/\___/\__,_/   
                                             Backend Service
    '''

if __name__ == '__main__':
    start_logo()
    start_ssh_pool()
    
    app.run(
        host='0.0.0.0', 
        port=7777,
        debug=True,
        use_reloader=False,
        threaded=True) 

    print 

    for k,v in nodes.iteritems():
        print ' * Closing connection {0}'.format(k)
        v['ssh'].close
