#include <string>

using namespace std;

const string URI = "mongodb://172.16.104.62:20001";
const string CONFIG = "config";
const string SHARDS = "shards";
const string CHUNKS = "chunks";
const string DB = "mydb";
const string COLLECTION = "score_list";

class Chunk {
 public:
  Chunk() {
  }

  Chunk(string a, string b, string c, string d) {
    ns = a;
    shard = b;
    minKey = c;
    maxKey = d;
  }
  
  void set(string a, string b, string c, string d) {
    ns = a;
    shard = b;
    minKey = c;
    maxKey = d;
  }

  string ns;
  string shard;
  string minKey;
  string maxKey;
};
