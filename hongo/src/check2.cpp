#include "include/config.hpp"

#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "mongo/bson/bson.h"
#include "mongo/client/dbclient.h"

using namespace std;

class Chunk;

mongo::DBClientConnection conn;

char quote = '"';
int chunk = 0;
map<string, string> shards;
vector<Chunk> chunks;


void getShardsMap() {
  auto_ptr<mongo::DBClientCursor> cursor = conn.query("config.shards");
  while (cursor->more()) {
    mongo::BSONObj o = cursor->next();
    string id = o.getStringField("_id");
    string host = o.getStringField("host");
    shards.insert(pair<string, string>(id, host));
  }

#ifdef debug
  for (map<string, string>::iterator it=shards.begin(); it!=shards.end(); ++it)
    cout << it->first << it->second << endl;
#endif

  return;
}

void getChunks() {
  auto_ptr<mongo::DBClientCursor> cursor = conn.query("config.chunks", mongo::BSONObj());
  while (cursor->more()) {
    mongo::BSONObj o = cursor->next();
    string ns = o.getStringField("ns");
    string shard = o.getStringField("shard");
    string min = o.getObjectField("min").jsonString();
    string max = o.getObjectField("max").jsonString();

    Chunk chunk;
    chunk.set(ns, shard, min, max);
    chunks.push_back(chunk);
  }

#ifdef debug
  for (int i=0; i<chunks.size(); i++) {
    cout << chunks[i].ns << endl
         << chunks[i].shard << endl
         << chunks[i].minKey << endl
         << chunks[i].maxKey << endl;
    mongo::BSONObj o = mongo::fromjson(chunks[i].minKey);
    cout << o.toString() << endl;
  }
#endif

  return;
}

void check(int pos) {
  mongo::Query query;
  query.minKey(mongo::fromjson(chunks[pos].minKey));
  query.maxKey(mongo::fromjson(chunks[pos].maxKey));

  auto_ptr<mongo::DBClientCursor> cursor = conn.query(chunks[pos].ns, query);
  while (cursor->more()) {
    mongo::BSONObj o = cursor->next();
    cout << o.toString() << endl;
  }

#ifdef debug
  cout << chunks[pos].ns << endl
       << chunks[pos].shard << endl;
#endif
  
  cout << query.toString() << endl;
  cout << conn.count(chunks[pos].ns, query) << endl;

  return;
}


int main(int argc, char* argv[]) {
  if (argc < 2) {
    cout << "Please input chunk number" << endl;
    return 1;
  }


  conn.connect("172.16.104.62:20001");

  getShardsMap();
  getChunks();
  
  check(stoi(argv[1]));

  return 0;
}
