# Author: legend
# Mail: legendlee1314@gmail.com
# File: hdfs2mongo_distributed.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
from bson.json_util import loads
from pymongo import MongoClient as mc
import pymongo
import pydoop.hdfs as hdfs
import zmq

import hashlib
import os
import re
import sys
import time


server_tcp = "tcp://*:20003"
client_tcp = "tcp://172.16.104.62:20003"
host_name = os.uname()[1]

mongo_host = 'mongodb://172.16.104.62:20001'
db = 'mydb'

def xml_from_hdfs(url):
    with hdfs.open(url, "r") as f:
        lines = f.read().strip().split('\n')
        docs, doc = [], None
        for line in lines:
            if line.startswith('<doc'):
                doc = line
            elif line.startswith('</doc>'):
                docs.append(doc + line)
            else:
                #line = line.replace('&', '').replace('"', "'")
                doc += line.replace('"', "'")

        for doc in docs:
            dom = bs(doc).find('doc')
            doc = {}
            try:
                doc['id'] = dom.attrs['id']
                doc['url'] = dom.attrs['url']
                doc['title'] = dom.attrs['title']
            except AttributeError, e:
                continue
            doc['content'] = dom.text
            doc['md5'] = hashlib.md5(str(doc)).hexdigest()
            yield doc

def write_to_mongo(docs, collection, dup=False):
    assert docs and collection 

    client = mc(mongo_host)
    collection = client[db][collection]

    count = 0

    for doc in docs:
        if dup is True:
            try:
                collection.insert_one(doc)
            except pymongo.errors.DuplicateKeyError, e:
                print e
        elif collection.find_one({'md5': doc['md5']}) is None:
                collection.insert_one(doc)

        count += 1

    time.sleep(1)
    print host_name + ' write ' + str(count)


def client():
    print 'Client...'
    #docs = xml_from_hdfs('/datasets/corpus/enwiki-11g')
    #write_to_mongo(docs, 'enwiki', True)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(client_tcp)
    socket.send("connect:" + host_name)
    message = socket.recv()
    if message != 'connected':
        return
    print 'Connected...'
    for request in range(100):
        socket.send("read:" + host_name)
        message = socket.recv()
        if message.startswith("done"):
            return
        else:
            f =  message.split('>')[1]
            print f
            docs = xml_from_hdfs(f)
            write_to_mongo(docs, 'enwiki', True)


def server():
    print 'Server...'
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(server_tcp)

    client_list = []
    hdfs_url = '/datasets/corpus/enwiki-11g'
    file_list = hdfs.ls(hdfs_url)
    print len(file_list)

    while True:
        message = socket.recv()
        if message.startswith("connect"):
            client_list.append(message.split(':')[1])
            socket.send("connected")
        elif message.startswith("read"):
            client = message.split(':')[1]
            print client
            if len(file_list) == 0:
                socket.send("done")
                client_list.remove(client)
                if len(client_list) == 0:
                    return
            if client in client_list:
                f = file_list.pop()
                print len(file_list)
                print f
                socket.send_string("file>" + f)



if __name__ == "__main__":
    if sys.argv[1] == 'server':
        server()
    else:
        client()
