"""
Add to PAM configuration with:
  auth    required    pam_python.so pam_crcauth.py

Requires configuration file, /etc/security/pam_crcauth.conf
"""

import syslog
import hashlib
import base64
import string
import sys
import grp, pwd 

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/etc/security/pam_crcauth.conf')

import MySQLdb
dbengineClass=MySQLdb

def pam_sm_authenticate(pamh, flags, argv):
    resp=pamh.conversation(
        pamh.Message(pamh.PAM_PROMPT_ECHO_OFF,"Password")
    )

    try:
        user = pamh.get_user(None)
    except pamh.exception, e:
        return e.pam_result
    if user == None:
        return pamh.PAM_USER_UNKNOWN

    groups = [g.gr_name for g in grp.getgrall() if 'crc-users' in g.gr_mem]
    if 'crc-users' not in groups:
        return pamh.PAM_SUCCESS

    try:
        def safeConfigGet(sect,key):
            if config.has_option(sect,key):
                return config.get(sect,key)
            else:
                None

        connargs={
            'mysqldb': { 
            'host': safeConfigGet('database','host'),
            'user': safeConfigGet('database','user'),
            'passwd': safeConfigGet('database','password'),
            'port': safeConfigGet('database','port'),
            'db': safeConfigGet('database','db')
            }
        }[dbengine]
    
        for k in connargs.keys():
            if connargs[k] is None:
                del connargs[k]
    
        db=dbengineClass.connect( **connargs )

        cursor=db.cursor()
        cursor.execute(config.get('query','select_statement'),(user))
        count_raw=cursor.fetchone()[0]

        if int(count_raw) == 1:
            syslog.syslog ("pam-crcauth.py match")
            return pamh.PAM_SUCCESS
        else:
            pamh.PAM_AUTH_ERR
    except:
        syslog.syslog ("pam-crcauth.py exception triggered")
        return pamh.PAM_SERVICE_ERR

    return pamh.PAM_SERVICE_ERR


def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
    return pamh.PAM_SUCCESS