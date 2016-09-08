# Author: legend
# Mail: legendlee1314@gmail.com
# File: mgr.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import re

# Env
hostname = os.uname()[1]

# Map
ip = {
  'master': '172.16.104.62',
  'w1': '172.16.104.1',
  'w2': '172.16.104.2',
  'w3': '172.16.104.3',
  'w4': '172.16.104.4',
  'w5': '172.16.104.5',
  'w6': '172.16.104.6',
  'w7': '172.16.104.7',
  'w8': '172.16.104.8',
  'w9': '172.16.104.9',
  'w10': '172.16.104.10',
  'w11': '172.16.104.11',
  'w12': '172.16.104.12',
  'w13': '172.16.104.13',
  'w14': '172.16.104.14',
  'w15': '172.16.104.15',
  'w16': '172.16.104.16',
  'w17': '172.16.104.17',
  'w18': '172.16.104.18',
  'w19': '172.16.104.19',
  'w20': '172.16.104.20'
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
  'config1': CONF_PATH + '/config1.conf',
  'config9': CONF_PATH + '/config9.conf',
  'config13': CONF_PATH + '/config13.conf',
  'config18': CONF_PATH + '/config18.conf',
  'route': CONF_PATH + '/route.conf',
  'route1': CONF_PATH + '/route1.conf',
  'route9': CONF_PATH + '/route9.conf',
  'route13': CONF_PATH + '/route13.conf',
  'route18': CONF_PATH + '/route18.conf',
}

R_C = ['worker1', 'worker9', 'worker13', 'worker18']

w_re = re.compile(r'worker(\d+)')

def print_cmd(cmd, tag=None):
    if not tag:
        print cmd
        return

    print '[{}] {}'.format(tag, cmd)

def run(mb, log, conf):
    cmd = '{} --logpath {} --config {}'.format(mb, log, conf) 
    print_cmd(cmd, tag='Run')
    print os.system(cmd)

def master():
    run(mb=mongod, log=MONGO_LOG + '/config.log', conf=CONFIG['config'])
    run(mb=mongos, log=MONGO_LOG + '/route.log', conf=CONFIG['route'])

def worker(w):
    run(mb=mongod, log=MONGO_LOG + '/{}.log'.format(w), conf=CONF_PATH + '/{}.conf'.format(w))

def route_config(w):
    if w not in R_C:
        return

    m = re.findall(w_re, w)
    if not m[0]:
        return

    w = m[0]
    run(mb=mongod, log=MONGO_LOG + '/config{}.log'.format(w), conf=CONFIG['config{}'.format(w)])
    run(mb=mongos, log=MONGO_LOG + '/route{}.log'.format(w), conf=CONFIG['route{}'.format(w)])

def mongo_shell(shell=None):
    if not shell:
        return

    cmd = '{} {}'.format(mongo, shell)
    print_cmd(cmd, tag='Run')
    print os.system(cmd)

def mongo_shell_with_auth(shell=None):
    if not shell:
        return

    cmd = '{} --shell --host {} --port {} admin -u root -p Husky'.format(mongo, shell.split(':')[0], shell.split(':')[1])
    print os.system(cmd)


def killall():
    processes = ['mongod', 'mongos']    
    for p in processes:
        cmd = 'pkill {}'.format(p)
        print_cmd(cmd, tag='Run')
        print os.system(cmd)

def create_all_users():
    servers = [ '172.16.104.' + str(i) for i in xrange(1, 21) ]
    for s in servers:
        c = '{} --host {} --port 20000 admin '.format(mongo, s)
        cmd = c + '--eval "db.getSiblingDB(\'admin\').createUser({user:\'root\',pwd:\'Husky\',roles:[\'root\']});"'
        print_cmd(cmd, tag='Run')
        print os.system(cmd)
        cmd = c + '--eval "db.getSiblingDB(\'hdb\').createUser({user:\'hdb_admin\',pwd:\'hdb_admin\',roles:[{role:\'readWrite\',db:\'hdb\'}]});"'
        print_cmd(cmd, tag='Run')
        print os.system(cmd)
        cmd = c + '--eval "db.getSiblingDB(\'hdb\').createUser({user:\'hdb\',pwd:\'hdb\',roles:[{role:\'read\',db:\'hdb\'}]});"'
        print_cmd(cmd, tag='Run')
        print os.system(cmd)

def for_all_servers():
    servers = [ '172.16.104.' + str(i) for i in xrange(1, 21) ]
    for s in servers:
        c = '{} --host {} --port 20000 admin -u root -p Husky '.format(mongo, s)
        cmd = c + '--eval "db.getSiblingDB(\'hdb\').dropUser(\'hdb_amin\');"'
        print_cmd(cmd, tag='Run')
        print os.system(cmd)
        cmd = c + '--eval "db.getSiblingDB(\'hdb\').createUser({user:\'hdb_admin\',pwd:\'hdb_admin\',roles:[{role:\'readWrite\',db:\'hdb\'}]});"'
        print_cmd(cmd, tag='Run')
        print os.system(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MongoDB Running Tools')
    parser.add_argument('-s', '--shell', help='Running MongoDB shell')
    parser.add_argument('-sa', '--shellauth', help='Running MongoDB shell with authentication')
    parser.add_argument('-r', '--run', help='Running machine', action='store_true')
    parser.add_argument('-rr', '--runroute', help='Running route', action='store_true')
    parser.add_argument('-ka', '--killall', help='Killall running processes', action='store_true')
    parser.add_argument('-c', '--create', help='Create users for each shard', action='store_true')
    parser.add_argument('-fa', '--forallservers', help='For all servers', action='store_true')
    args = parser.parse_args()

    if args.shell:
        mongo_shell(args.shell)
    elif args.shellauth:
        mongo_shell_with_auth(args.shellauth)

    if args.killall:
        killall()

    if args.create:
        create_all_users()

    if args.forallservers:
        for_all_servers()

    if args.run:
        assert hostname
        if hostname == 'master':
            master()
        else:
            worker(hostname)

    if args.runroute:
        assert hostname
        route_config(hostname)
