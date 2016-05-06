#include "include/config.hpp"

#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/json.hpp>

#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>

using namespace std;

class Chunk;

bsoncxx::types::b_minkey minkey;
bsoncxx::types::b_maxkey maxkey;
mongocxx::instance inst{};
mongocxx::client conn{mongocxx::uri{URI}};

char quote = '"';
int chunk = 0;
map<string, string> shards;
vector<Chunk> chunks;

string removeQuotes(string &str) {
  str.erase(remove(str.begin(), str.end(), quote), str.end());
  return str;
}

void getShardsMap() {
  auto config = conn[CONFIG][SHARDS];
  auto cursor = config.find({});
  for (auto&& doc : cursor) {
    string id = bsoncxx::to_json(doc["_id"].get_value());
    string host = bsoncxx::to_json(doc["host"].get_value());
    shards.insert(pair<string, string>(removeQuotes(id), removeQuotes(host)));
  }

#ifdef debug
  for (map<string, string>::iterator it=shards.begin(); it!=shards.end(); ++it)
    cout << it->first << it->second << endl;
#endif

  return;
}

void getChunks() {
  auto config = conn[CONFIG][CHUNKS];
  auto cursor = config.find({});
  for (auto&& doc : cursor) {
    string ns = bsoncxx::to_json(doc["ns"].get_value());
    string shard = bsoncxx::to_json(doc["shard"].get_value());
    string min = bsoncxx::to_json(doc["min"]["id"].get_value());
    string max = bsoncxx::to_json(doc["max"]["id"].get_value());

    Chunk chunk;
    if (doc["min"]["id"].get_value() == minkey) {
      chunk.set(removeQuotes(ns), removeQuotes(shard), "", removeQuotes(max));
    } else if (doc["max"]["id"].get_value() == maxkey) {
      chunk.set(removeQuotes(ns), removeQuotes(shard), removeQuotes(min), "");
    } else {
      chunk.set(removeQuotes(ns), removeQuotes(shard), removeQuotes(min), removeQuotes(max));
    }
    chunks.push_back(chunk);
  }

#ifdef debug
  for (int i=0; i<chunks.size(); i++) {
    cout << chunks[i].ns << endl
         << chunks[i].shard << endl
         << chunks[i].minKey << endl
         << chunks[i].maxKey << endl;
  }
#endif

  return;
}

void check(int pos) {
  bsoncxx::builder::stream::document query;
  if (chunks[pos].minKey.empty()) {
    query << "id" << bsoncxx::builder::stream::open_document << "$lt" << stoi(chunks[pos].maxKey) << bsoncxx::builder::stream::close_document;
  } else if (chunks[pos].maxKey.empty()) {
    query << "id" << bsoncxx::builder::stream::open_document << "$gte" << stoi(chunks[pos].minKey) << bsoncxx::builder::stream::close_document;
  } else {
    query << "id" << bsoncxx::builder::stream::open_document << "$gte" << stoi(chunks[pos].minKey) << "$lt" << stoi(chunks[pos].maxKey) << bsoncxx::builder::stream::close_document;
  }

  cout << bsoncxx::to_json(query) << endl;

  mongocxx::options::find opts;
  opts.limit(5);
  auto collection = conn[DB][COLLECTION];
  auto cursor = collection.find(query.view(), opts);
  
  for (auto&& doc : cursor) {
    cout << bsoncxx::to_json(doc) << endl;
  }

#ifdef debug
  cout << chunks[pos].ns << endl
       << chunks[pos].shard << endl;
#endif

  cout << collection.count(query.view()) << endl;

  return;
}


int main(int argc, char* argv[]) {
  if (argc < 2) {
    cout << "Please input chunk number" << endl;
    return 1;
  }

  getShardsMap();
  getChunks();

  check(stoi(argv[1]));

  return 0;
}
