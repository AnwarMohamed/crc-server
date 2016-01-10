#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, abort
from flask.ext.basicauth import BasicAuth
from flask.ext.mysql import MySQL


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



@app.route('/api/v1/vm/<node_name>/status', methods=['GET'])
def api_vm_status(node_name):    
    abort(400)

@app.route('/api/v1/vm/<node_name>/start', methods=['POST'])
def api_vm_start(node_name):        
    abort(400)

@app.route('/api/v1/vm/<node_name>/stop', methods=['POST'])
def api_vm_stop(node_name):        
    abort(400)

@app.route('/api/v1/vm/<node_name>/reset', methods=['POST'])
def api_vm_reset(node_name):        
    abort(400)



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



if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=7777,
        debug=True,
        threaded=True) 
        #ssl_context='adhoc')
