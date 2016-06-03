# Author: legend
# Mail: legendlee1314@gmail.com
# File: hdfs2mongo.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient as mc
from bson.json_util import loads
import pydoop.hdfs as hdfs

import hashlib
import time

host = 'mongodb://172.16.104.62:20001'

def read_from_hdfs(url):
    assert hdfs.path.isdir(url)
    file_lists = hdfs.ls(url)
    for fi in file_lists:
        with hdfs.open(fi, "r") as f:
            items = f.read()
            items = items.strip().split('\n')
            for it in items:
                it = loads(it)
                it['md5'] = hashlib.md5(str(it)).hexdigest()
                yield it

def write_to_mongo(docs):
    assert docs

    client = mc(host)
    collection = client['mydb']['openrice']

    count = 0

    for doc in docs:
        if collection.find_one({'md5': doc['md5']}) is None:
            collection.insert_one(doc)
            print 'Inserted #%s...' % count
            count += 1

    time.sleep(10)

    print collection.count()
    assert collection.count() == count

if __name__ == "__main__":
    docs =  read_from_hdfs('/datasets/crawl/openrice')
    write_to_mongo(docs)
