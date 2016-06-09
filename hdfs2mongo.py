# Author: legend
# Mail: legendlee1314@gmail.com
# File: hdfs2mongo.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
from bson.json_util import loads
from pymongo import MongoClient as mc
import pydoop.hdfs as hdfs

import hashlib
import re
import time


host = 'mongodb://172.16.104.62:20001'
db = 'hdb'
username = 'hdb_admin'

def json_from_hdfs(url):
    assert hdfs.path.isdir(url)
    file_lists = hdfs.ls(url)
    for fi in file_lists:
        with hdfs.open(fi, "r") as f:
            items = f.read().strip().split('\n')
            for it in items:
                it = loads(it)
                it['md5'] = hashlib.md5(str(it)).hexdigest()
                yield it

def xml_from_hdfs(url):
    assert hdfs.path.isdir(url)
    file_lists = hdfs.ls(url)
    #for fi in file_lists:
    for i in xrange(0, 1):
        fi = '/datasets/corpus/enwiki-11g/wiki_912'
        with hdfs.open(fi, "r") as f:
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
                doc = dom.attrs
                doc['content'] = dom.text
                doc['md5'] = hashlib.md5(str(doc)).hexdigest()
                yield doc

def write_to_mongo(docs, collection, dup=False):
    assert docs and collection 

    client = mc(host)
    database = client[db]
    database.authenticate(username, password=username)
    collection = database[collection]

    count = 0

    for doc in docs:
        if dup is True:
            collection.insert_one(doc)
        elif collection.find_one({'md5': doc['md5']}) is None:
            collection.insert_one(doc)

        print 'Inserted #%s...' % count
        count += 1

    time.sleep(30)

    print collection.count()
    assert collection.count() == count

def main():
    docs =  json_from_hdfs('/datasets/crawl/openrice')
    write_to_mongo(docs, 'openrice')
    #docs = xml_from_hdfs('/datasets/corpus/enwiki-11g')
    #write_to_mongo(docs, 'enwiki', True)

if __name__ == "__main__":
    main()
