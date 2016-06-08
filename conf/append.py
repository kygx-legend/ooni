#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

files = [ 'worker' + str(i) for i in xrange(1, 21) ]
#files += ['route']
#files += ['config']

for f in files:
    os.system('cat a.conf >> {}.conf'.format(f))
