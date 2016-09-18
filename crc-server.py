#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    #filename='/var/log/crc-service.log',
    level=logging.INFO, 
    datefmt='%Y-%m-%d %H:%M:%S')

from flask import Flask, jsonify, abort, request
from flask.ext.basicauth import BasicAuth
from flask.ext.mysql import MySQL
from paramiko.client import SSHClient
from paramiko import AutoAddPolicy
from subprocess import call,Popen
import threading, os, random, string, portalocker , signal,base64
import time, thread, schedule
from decorators import *

app = Flask(__name__)
#app.config['BASIC_AUTH_USERNAME'] = 'crc-user'
#app.config['BASIC_AUTH_PASSWORD'] = 'crc-pass'
#app.config['BASIC_AUTH_FORCE'] = True
#basic_auth = BasicAuth(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'PORTAL'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

frisbee_log_path="/usr/local/share/frisbee_tasks/"
experiments_log_path="/usr/local/share/experiments/"

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

vms_mapping = {}

def start_vm_mapping():
    conn = mysql.connect()
    cursor = conn.cursor()
    sql_str="""select vm_name,hv_name,physical_name from 
    (
        select vm_name,hv_name, node_ip as physical_name  
        from  PORTAL.portal_simulationvm join PORTAL.portal_physicalnode 
        where PORTAL.portal_physicalnode.id=100
    ) as sim
    union 
    select vm_name,hv_name,physical_name from 
    (
        select vm_name,hv_name, node_ip as physical_name  
        from  PORTAL.portal_virtualnode 
        join PORTAL.portal_physicalnode 
        where PORTAL.portal_virtualnode.node_ref_id=PORTAL.portal_physicalnode.id
    ) as tst; """
    cursor.execute(sql_str)
    conn.commit()

    results = cursor.fetchall()
    #print results
    for row in results:
        #print row
        vms_mapping[row[0]] = [row[1],row[2]]
        
    #print vms_mapping['node1w']

    cursor.close()
    conn.close()

@app.route('/api/v1/vm/<vm_name>/status', methods=['GET'])
@crossdomain(origin='*')
def api_vm_status(vm_name):
    global nodes
    if vm_name not in vms_mapping:
        abort(400)
    else:
        try:            
            vm_data=vms_mapping[vm_name]
            vm_internal_name = vm_data[0]
            physical_name = vm_data[1]
            
            client = nodes[physical_name]['ssh']
            ip = nodes[physical_name]['ip']

            if not check_ssh_alive(client) and not reconnect_ssh(client, ip, False):
                response = {'message': 'Node is unavailable'}
                response = jsonify(response)
                return response, 503

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


def vm_start(vm_name):
    global nodes  

    vm_data=vms_mapping[vm_name]
    vm_internal_name = vm_data[0]
    physical_name = vm_data[1]
            
    client = nodes[physical_name]['ssh']
    ip = nodes[physical_name]['ip']

    if not check_ssh_alive(client) and not reconnect_ssh(client, ip, False):
        return None    

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        return None

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        client.exec_command('VBoxManage startvm {0} --type headless'.format(vm_internal_name)) 


@app.route('/api/v1/vm/<vm_name>/start', methods=['POST'])
@crossdomain(origin='*')
def api_vm_start(vm_name):        
    global nodes
    if vm_name not in vms_mapping:
        abort(400)
    else:
        thread = threading.Thread(
            target=vm_start, 
            args=(vm_name,))
        thread.start()

    return ''


def vm_stop( vm_name):
    global nodes   
    vm_data=vms_mapping[vm_name]
    vm_internal_name = vm_data[0]
    physical_name = vm_data[1]
            
    client = nodes[physical_name]['ssh']
    ip = nodes[physical_name]['ip']

    if not check_ssh_alive(client) and not reconnect_ssh(client, ip, False):
        return None    

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        return None

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) > 0:
        client.exec_command('VBoxManage controlvm {0} poweroff soft'.format(vm_internal_name)) 


@app.route('/api/v1/vm/<vm_name>/stop', methods=['POST'])
@crossdomain(origin='*')
def api_vm_stop(vm_name):        
    global nodes
    if vm_name not in vms_mapping:
        abort(400)
    else:
        thread = threading.Thread(
            target=vm_stop, 
            args=(vm_name,))
        thread.start() 

    return ''      


def vm_reset(vm_name):
    global nodes   

    vm_data=vms_mapping[vm_name]
    vm_internal_name = vm_data[0]
    physical_name = vm_data[1]
            
    client = nodes[physical_name]['ssh']
    ip = nodes[physical_name]['ip']

    if not check_ssh_alive(client) and not reconnect_ssh(client, ip, False):
        return None    

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
@crossdomain(origin='*')
def api_vm_reset(vm_name):        
    global nodes
    if vm_name not in vms_mapping:
        return abort(400)
    else:
        thread = threading.Thread(
            target=vm_reset, 
            args=(vm_name,))        
        thread.start() 

    return ''


def vm_reset2(vm_name):
    global nodes   

    vm_data=vms_mapping[vm_name]
    vm_internal_name = vm_data[0]
    physical_name = vm_data[1]
            
    client = nodes[physical_name]['ssh']
    ip = nodes[physical_name]['ip']

    if not check_ssh_alive(client) and not reconnect_ssh(client, ip, False):
        return None

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list vms | grep -w {0}'.format(vm_internal_name))

    if len(stdout.read()) == 0:
        return None

    stdin, stdout, stderr = client.exec_command(
        'VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))
    
    if len(stdout.read()) == 0:
        client.exec_command('VBoxManage startvm {0} --type headless'.format(vm_internal_name)) 
    else:
        client.exec_command('VBoxManage controlvm {0} acpipowerbutton'.format(vm_internal_name))
        print "Issued ACPI shutdown"
        stdin, stdout, stderr = client.exec_command('VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))
        
        n_attempts=0
        ret='emp' 
        while len(ret) != 0:
            time.sleep(1)
            print "Checking if node is off"
            stdin, stdout, stderr = client.exec_command('VBoxManage list runningvms | grep -w {0}'.format(vm_internal_name))
            ret=stdout.read()
            if n_attempts>=10:
                print "Forcing shutdown"
                client.exec_command('VBoxManage controlvm {0} poweroff'.format(vm_internal_name)) 
                break
            
            n_attempts= n_attempts + 1
        print "Node is off waiting 3 seconds"
        
        time.sleep(3)
        print "Starting node"
        client.exec_command('VBoxManage startvm {0} --type headless'.format(vm_internal_name)) 


@app.route('/api/v1/vm/<vm_name>/reset2', methods=['POST'])
@crossdomain(origin='*')
def api_vm_reset2(vm_name):        
    global nodes
    if vm_name not in vms_mapping:
        return abort(400)
    else:
        thread = threading.Thread(
            target=vm_reset2, 
            args=(vm_name,))        
        thread.start() 

    return ''


def image_load(name, path, node_list, task_id_list):   
    for task_id in task_id_list:
        call(["rm", "-rf", frisbee_log_path+"{0}-load.progress".format(task_id)])  
        print(" ".join(["rm", "-rf", frisbee_log_path+"{0}-load.progress".format(task_id)])) 
        call(["rm", "-rf", frisbee_log_path+"{0}-load.lock".format(task_id)]) 
        call(["rm", "-rf", frisbee_log_path+"{0}-load.error".format(task_id)]) 
        call(["mkdir", "-p", frisbee_log_path])
        call(["touch",frisbee_log_path+ "{0}-load.lock".format(task_id)])
        call(["touch",frisbee_log_path+"{0}-load.progress".format(task_id)])

    print " ".join(["omf_load.sh", "{0}".format(','.join(node_list)), "{0}".format(name), "{0}".format(','.join(task_id_list))])
    call(["omf_load.sh", "{0}".format(','.join(node_list)), "{0}".format(name), "{0}".format(','.join(task_id_list))])
    for task_id in task_id_list:
        call(["rm", frisbee_log_path+"{0}-load.lock".format(task_id)])

@app.route('/api/v1/image/load', methods=['POST'])
@crossdomain(origin='*')
def api_image_load():

    json_req = request.get_json(force=True, silent=True)
    json_params = ['name', 'path', 'nodes_list', 'task_id']

    if json_req == None or any(param not in json_req for param in json_params):            
        return abort(400)

    if os.path.exists(json_req['path']) == False:
        return abort(400)

    thread = threading.Thread(
        target=image_load, 
        args=(json_req['name'], json_req['path'], json_req['nodes_list'], json_req['task_id']))
    thread.start()

    return jsonify({'task_id': json_req['task_id']})

last_progress="0"
@app.route('/api/v1/image/load/<task_id>', methods=['GET'])
@crossdomain(origin='*')
def api_image_load_status(task_id):        

    progress_log = frisbee_log_path+"{0}-load.progress".format(task_id)
    error_log = frisbee_log_path+"{0}-load.error".format(task_id)    
    lock_path = frisbee_log_path+"{0}-load.lock".format(task_id)
    
    if os.path.exists(progress_log) == False:
        return abort(400)
    global last_progress
    if os.stat(progress_log).st_size > 0:
        progress = last_progress
        with open(progress_log, 'r') as plog:
          for line in plog:
             pass
          line_split=line.split(" ")
          if len(line_split)>=2:
             progress_perc = line.split(" ")[1]
             if progress_perc[-1] == '%':
                  progress=progress_perc[:-1] 
                  last_progress = progress   
    else:
        progress="0"
        last_progress="0"  


    return jsonify({
        'task_id': task_id,
        'progress': progress,
        'error': os.path.exists(error_log),
        'done': not os.path.exists(lock_path)
    })


def image_save(name, path, node_list, task_id):    
    call(["rm", "-rf", frisbee_log_path+"{0}-save.*".format(task_id)])
    call(["mkdir", "-p", frisbee_log_path])
    call(["touch", frisbee_log_path+"{0}-save.lock".format(task_id)])
    call(["omf_save.sh", "{0}".format(','.join(node_list)), "{0}".format(name), "{0}".format(task_id)])
    call(["rm", "-rf", frisbee_log_path+"{0}-save.lock".format(task_id)])

@app.route('/api/v1/image/save', methods=['POST'])
@crossdomain(origin='*')
def api_image_save():        

    json_req = request.get_json(force=True, silent=True)
    json_params = ['name', 'path', 'nodes_list', 'task_id']

    if json_req == None or any(param not in json_req for param in json_params):            
        return abort(400)

    if os.path.exists(json_req['path']) == False:
        return abort(400)

    thread = threading.Thread(
        target=image_save, 
        args=(json_req['name'], json_req['path'], json_req['nodes_list'], json_req['task_id']))
    thread.start()

    return jsonify({'task_id': json_req['task_id']})


@app.route('/api/v1/image/save/<task_id>', methods=['GET'])
@crossdomain(origin='*')
def api_image_save_status(task_id):

    progress_log = frisbee_log_path+"{0}-save.progress".format(task_id)
    error_log = frisbee_log_path+"{0}-save.error".format(task_id)    
    lock_path = frisbee_log_path+"{0}-save.lock".format(task_id)
    
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
        'error': os.path.exists(error_log),
        'done': not os.path.exists(lock_path)
    })



@app.route('/api/v1/user/', methods=['POST'])
@crossdomain(origin='*')
def api_user_create():     

    json_req = request.get_json(force=True, silent=True)
    json_params = ['username', 'password']

    if json_req == None or any(param not in json_req for param in json_params):            
        return abort(400)

    print json_req

    call(["/home/crc-admin/crc-server/user_add.sh", json_req['username'], json_req['password']])

    return ''

@app.route('/api/v1/user/<user_name>', methods=['DELETE'])
@crossdomain(origin='*')
def api_user_delete(user_name):    
    
    FNULL = open(os.devnull, 'w')
    call(["./user_delete.sh", user_name], stdout=FNULL, stderr=FNULL)    

    return ''

def experiment_execute(exp_id, script,username):
    call(["rm", "-rf", experiments_log_path+"{0}.*".format(exp_id)])
    call(["touch", experiments_log_path+"{0}.lock".format(exp_id)])
    call(["mkdir", "-p", "/home/crc-users/{0}/scripts".format(username)])  
    log_file = open(experiments_log_path+"{0}.log".format(exp_id), "w+") 

    with open("/home/crc-users/{0}/scripts/{1}".format(username, exp_id), 'w') as file_:
        file_.write(base64.b64decode(script))

    #call(["omf_ec", "-u" ,"amqp://10.0.0.200",  "exec",  "--oml_uri", "tcp:10.0.0.200:3003", path,"& ", "echo", "$!", ">", "experiments/{0}.pid".format(exp_id)], stdout=log_file)

    p=Popen(["omf_ec", "-u" ,"amqp://10.0.0.200",  "exec",  "--oml_uri", "tcp:10.0.0.200:3003", "/home/crc-users/{0}/scripts/{1}".format(username, exp_id)], stdout=log_file)
    with open(experiments_log_path+"{0}.pid".format(exp_id), "w") as pid_file:
        pid_file.write(format(p.pid))                
    p.wait()

    log_file.close()

    call(["rm", "-rf", experiments_log_path+"{0}.lock".format(exp_id)])

@app.route('/api/v1/experiment/', methods=['POST'])
@crossdomain(origin='*')
def api_experiment_execute(): 
    
    json_req = request.get_json(force=True, silent=True)

    if json_req == None or 'script' not in json_req or 'username' not in json_req:
        return abort(400)            

    exp_id = ''.join(random.SystemRandom()
        .choice(string.ascii_uppercase + string.digits) for _ in range(12))

    thread = threading.Thread(
        target=experiment_execute, 
        args=(exp_id, json_req['script'], json_req['username']))        
    thread.start()

    return jsonify({'exp_id': exp_id})


@app.route('/api/v1/experiment/<exp_id>', methods=['DELETE'])
@crossdomain(origin='*')
def api_experiment_delete(exp_id):
    
    pid_path = experiments_log_path+"{0}.pid".format(exp_id)

    if os.path.exists(pid_path) == False:
        return abort(400)

    try:                
        #call(["cat", "experiments/{0}.pid".format(exp_id), "|","xargs", "kill", "-9"])
        with open(experiments_log_path+"{0}.pid".format(exp_id), 'r') as pid_file:
           pid=int(pid_file.readline().rstrip('\n'))
        os.kill(pid, signal.SIGTERM)
        return ''
    except:
        return abort(400)


@app.route('/api/v1/experiment/<exp_id>', methods=['GET'])
@crossdomain(origin='*')
def api_experiment_status(exp_id):

    frisbee_log_path = experiments_log_path+"{0}.log".format(exp_id)
    lock_path = experiments_log_path+"{0}.lock".format(exp_id)

    if os.path.exists(frisbee_log_path) == False:
        return abort(400)

    try:
        log = []

        if os.path.exists(lock_path) == False:
            status = 'finished'
        else:
            status = 'running'

        with open(experiments_log_path+"{0}.log".format(exp_id), 'r') as log_file:            
            for line in log_file:
                log.append(line.rstrip())

        return jsonify({
            'status': status, 
            'log': log,
            'done': not os.path.exists(lock_path)
            })
    except:
        abort(400)

def authorize_ssh_sessions():
    conn = mysql.connect()
    cursor = conn.cursor()
        
    cursor.execute("""
    	select username from portal_reservation 
    	inner join portal_myuser as user 
    	on user_ref_id=user.id 
    	where NOW() not between f_start_time and f_end_time
    	""")
    conn.commit()

    results = cursor.fetchall()
    for row in results:
    	print "Kicking {0}".format(row[0])
        call(["skill", "-KILL", "-u", row[0]])

    cursor.close()
    conn.close()

def ssh_monitor_sessions():
    schedule.every().hour.do(authorize_ssh_sessions)

    while True:
        schedule.run_pending()
        time.sleep(1)

def start_ssh_monitor():
    thread.start_new_thread(ssh_monitor_sessions, ())        

def check_ssh_alive(client):
    transport = client.get_transport()

    if transport != None and transport.is_active():
        try:
            client.exec_command('uname')
            return True
        except:
            return False
    else:
        return False

def reconnect_ssh(client, ip, retry):
    while True:
        try:
            client.connect(ip, username='node5', password='crc123')
            return True
        except:     
            if retry == True:
                time.sleep(30)                              
            else:
                return False

def connect_ssh(client, ip, node):
    try:
        client.connect(ip, username='node5', password='crc123')
        print ' * Connected to {0} @ {1}'.format(node, ip)
    except Exception, e:
        print ' * Failed to connect to {0} @ {1}'.format(node, ip)

        time.sleep(30)
        reconnect_ssh(client, ip, True)

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
#            client.get_transport().set_keepalive(10)            
            client.set_missing_host_key_policy(AutoAddPolicy())

            thread.start_new_thread(connect_ssh, (client, v['ip'], k))

            nodes[k]['ssh'] = client        

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
    start_vm_mapping()
    start_ssh_pool()
    start_ssh_monitor()
    
    app.run(
        host='0.0.0.0', 
        port=7777,
        debug=True,
        use_reloader=False,
        threaded=True) 

    print 

    for k,v in nodes.iteritems():        
        if check_ssh_alive(v['ssh']):
            print ' * Closing connection {0}'.format(k)            
            v['ssh'].close
