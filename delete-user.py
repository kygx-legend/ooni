# Author: legend
# Mail: kygx.legend@gmail.com
# File: delete-user.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import re

def print_cmd(cmd, tag=None):
    if not tag:
        print cmd
        return

    print '[{}] {}'.format(tag, cmd)

def run(cmd):
    print_cmd(cmd, tag='Run')
    print os.system(cmd)

def delete_user(name):
    cmd = 'sudo userdel -r {}'.format(name)
    run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete User')
    parser.add_argument('-name', '--username', help='User Name')
    args = parser.parse_args()

    if args.username:
        delete_user(args.username)
