#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.basicauth import BasicAuth
from flask.ext.mysql import MySQL


app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'crc-user'
app.config['BASIC_AUTH_PASSWORD'] = 'crc-pass'
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'crc-server'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)


@app.route('/api/v1/', methods=['GET'])
def api_method():
    conn = shared.mysql.connect()
    cursor = conn.cursor()
    
    response = {}

    return jsonify(response) 


if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=7777,
        debug=True,
        threaded=True) 
        #ssl_context='adhoc')
