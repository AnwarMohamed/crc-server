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
import traceback

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/etc/security/pam_crcauth.conf')

import MySQLdb
dbengineClass=MySQLdb

def pam_sm_authenticate(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
    try:
        user = pamh.get_user(None)
    except pamh.exception, e:
        return e.pam_result
    if user == None:
        return pamh.PAM_USER_UNKNOWN

    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]    
    gid = pwd.getpwnam(user).pw_gid
    groups.append(grp.getgrgid(gid).gr_name)

    if 'crc-users' not in groups:
        return pamh.PAM_SUCCESS

    try:
        def safeConfigGet(sect,key):
            if config.has_option(sect,key):
                return config.get(sect,key)
            else:
                None

        connargs = {
            'mysqldb': { 
            'host': safeConfigGet('database','host'),
            'user': safeConfigGet('database','user'),
            'passwd': safeConfigGet('database','password'),
            'port': int(safeConfigGet('database','port')),
            'db': safeConfigGet('database','db')
            }
        }['mysqldb']
    
        for k in connargs.keys():
            if connargs[k] is None:
                del connargs[k]
    
        db = dbengineClass.connect( **connargs )

        syslog.syslog ("checking user: {0}".format(user))

        cursor=db.cursor()
        cursor.execute("select count(*) from slices where user_name='{0}' and NOW() between start_time and end_time".format(user))
        count_raw=cursor.fetchone()[0]

        if int(count_raw) == 1:
            syslog.syslog ("pam-crcauth.py succeed")
            return pamh.PAM_SUCCESS
        else:
            syslog.syslog ("pam-crcauth.py failed")
            return pamh.PAM_ACCT_EXPIRED

    except Exception, e:
        syslog.syslog ("pam-crcauth.py exception triggered")
        syslog.syslog (traceback.format_exc())
        return pamh.PAM_SERVICE_ERR

    return pamh.PAM_SERVICE_ERR

def pam_sm_open_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
    return pamh.PAM_SUCCESS