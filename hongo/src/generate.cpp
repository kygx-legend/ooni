#include "include/config.hpp"

#include <cstdlib>
#include <iostream>

#include <bsoncxx/builder/stream/document.hpp>

#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>

using namespace std;


string lowers = "abcdefghijklmnopqrstuvwxyz";
string capitals = "ABCEDFGHIJKLMNOPQRSTUVWXYZ";

mongocxx::instance inst{};
mongocxx::client conn{mongocxx::uri{URI}};

const int counts = 10000;


string genName() {
  int first_length = rand() % 3 + 5;
  int last_length = rand() % 3 + 5;
  
  string first_name;
  for (int i=0; i<first_length; i++) {
    if (i == 0) {
      first_name.push_back(capitals[rand() % 26]);
      continue;
    }
    first_name.push_back(lowers[rand() % 26]);
  }

  string last_name;
  for (int i=0; i<last_length; i++) {
    if (i == 0) {
      last_name.push_back(capitals[rand() % 26]);
      continue;
    }
    last_name.push_back(lowers[rand() % 26]);
  }

  return first_name + " " + last_name;
}

string genText(int count) {
  string str;
  for (int i=0; i<count; i++) {
    str.push_back(lowers[rand() % 26]);
  }
  return str;
}

void genDocs() {
  auto collection = conn[DB][COLLECTION];
  int64_t count = collection.count({});
  if (count >= counts) {
    cout << "Already generated!" << endl;
    return;
  }

  int id = 10001;
  for (int i=0; i<counts; i++) {
    bsoncxx::builder::stream::document document{};
    document << "id" << bsoncxx::types::b_int32{id + i};
    document << "name" << genName();
    document << "result" << bsoncxx::types::b_int32{rand() % 50 + 50};
    document << "text" << genText(100);
    collection.insert_one(document.view());
  }

  count = collection.count({});
  if (count == counts) {
    cout << "Generate sucessfully!" << endl;
  } else {
    cout << "Generate failed!" << endl;
  }

  return;
}

int remove() {
  auto collection = conn[DB][COLLECTION];
  collection.delete_many({});

  int64_t count = collection.count({});
  if (count != 0) {
    cout << "Remove failed!" << endl;
    return 1;
  }

  cout << "Remove sucessfully!" << endl;
  return 0;
}


int main(int argc, char* argv[]) {
  if (stoi(argv[1]) == 0) {
    return remove();
  }
  genDocs();

  return 0;
}
