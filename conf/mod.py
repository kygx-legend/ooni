#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

files = [ 'worker' + str(i) for i in xrange(1, 21) ]
#files += ['route']
#files += ['config']

def append():
    for f in files:
        os.system('cat a.conf >> {}.conf'.format(f))

def remove():
    a = open('a.conf', 'r').readlines()
    a = '\n'.join([i.rstrip() for i in a])
    for f in files:
        with open(f + '.conf', 'r') as fi:
            b = fi.readlines()
            b = '\n'.join([i.rstrip() for i in b])
            b = b.replace(a, '')
            fi = open(f + '.conf', 'w')
            fi.write(b)

append()
#remove()
