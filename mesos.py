# Author: legend
# Mail: kygx.legend@gmail.com
# File: mesos.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import re

MASTER_IP = '172.16.104.62'

MESOS_PATH = '/data/opt/mesos-1.4.0/build'
WORK_DIR = '/tmp/mesos/work_dir'

MASTER_SH = 'bin/mesos-master.sh'
WORKER_SH = 'bin/mesos-agent.sh'

def print_cmd(cmd, tag=None):
    if not tag:
        print cmd
        return

    print '[{}] {}'.format(tag, cmd)

def run(cmd):
    cmd = '{} --work_dir={}'.format(cmd, WORK_DIR)
    print_cmd(cmd, tag='Run')
    print os.system(cmd)

def run_master():
    run('{} --ip={}'.format(os.path.join(MESOS_PATH, MASTER_SH), MASTER_IP))

def run_agent():
    run('{} --master={}:5050'.format(os.path.join(MESOS_PATH, WORKER_SH), MASTER_IP))

def kill_master():
    cmd = 'pkill lt-mesos-master'
    print_cmd(cmd, tag='Run')
    print os.system(cmd)

def kill_agent():
    cmd = 'pkill lt-mesos-agent'
    print_cmd(cmd, tag='Run')
    print os.system(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mesos Cluster Tools')
    parser.add_argument('-rm', '--runmaster', help='Run master', action='store_true')
    parser.add_argument('-ra', '--runagent', help='Run agent', action='store_true')
    parser.add_argument('-km', '--killmaster', help='Kill master', action='store_true')
    parser.add_argument('-ka', '--killagent', help='Kill agent', action='store_true')
    args = parser.parse_args()

    if args.runmaster:
        run_master()
    if args.runagent:
        run_agent()
    if args.killmaster:
        kill_master()
    if args.killagent:
        kill_agent()
