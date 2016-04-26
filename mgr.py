# Author: legend
# Mail: legendlee1314@gmail.com
# File: mgr.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os

# Env
hostname = os.uname()[1]

# Map
ip = {
  'master': '172.16.104.62',
  'w1': '172.16.104.1',
  'w2': '172.16.104.2',
  'w3': '172.16.104.3'
}

# Path
PATH = '/data'
CONF_PATH = os.getcwd() + '/conf'
MONGO_BIN_PATH = PATH + '/opt/mongo-tools/bin'
MONGO_PATH = PATH + '/legend'
MONGO_DATA = MONGO_PATH + '/db'
MONGO_LOG = MONGO_PATH + '/log'

# Mongo Bin
mongo = MONGO_BIN_PATH + '/mongo' 
mongod = MONGO_BIN_PATH + '/mongod'
mongos = MONGO_BIN_PATH + '/mongos'

# File

CONFIG = {
  'config': CONF_PATH + '/config.conf',
  'route': CONF_PATH + '/route.conf',
  's1': CONF_PATH + '/s1.conf',
  's2': CONF_PATH + '/s2.conf',
  's3': CONF_PATH + '/s3.conf',
}

def run(mb, log, conf):
    cmd = '{} --logpath {} --config {}'.format(mb, log, conf) 
    print cmd
    print os.system(cmd)

def master():
    run(mb=mongod, log=MONGO_LOG + '/config.log', conf=CONFIG['config'])
    run(mb=mongos, log=MONGO_LOG + '/route.log', conf=CONFIG['route'])

def w1():
    run(mb=mongod, log=MONGO_LOG + '/s1.log', conf=CONFIG['s1'])

def w2():
    run(mb=mongod, log=MONGO_LOG + '/s2.log', conf=CONFIG['s2'])

def w3():
    run(mb=mongod, log=MONGO_LOG + '/s2.log', conf=CONFIG['s2'])

def start():
    pass

def shutdown():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='Running machine hostname')
    args = parser.parse_args()

    if args.host == 'master':
        master()
    elif args.host == 'w1':
        w1()
    elif args.host == 'w2':
        w2()
    elif args.host == 'w3':
        w3()
    else:
        print 'Dry run'
