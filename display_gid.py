#!/usr/bin/env python2
import os

print "uid: %s" % os.getuid()
print "euid: %s" % os.geteuid()
print "gid: %s" % os.getgid()
print "egid: %s" % os.getegid()
