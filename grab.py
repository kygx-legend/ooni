# Author: legend
# Mail: kygx.legend@gmail.com
# File: grab.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import requests

from bs4 import BeautifulSoup as soup
from pymongo import MongoClient as mc


head = 'http://www.nba.com'
host = 'mongodb://172.16.104.62:20001'


def getLinks():
  cache = open('links.tmp', 'a')

  navigation = '{}/2016/news/archive/{}/index.html'
  for week in xrange(10, 20):
    req = requests.get(navigation.format(head, week))
    page = soup(req.text, 'html.parser')
    div = page.find('div', class_='nbaNAContent')
    div = '<html><body>{}</body></html>'.format(str(div)) 
    links = soup(div, 'html.parser').find_all('a')
    for l in links:
      cache.write(l.get_text() + '\n')
      cache.write(l.get('href') + '\n')


def getNews():
  client = mc(host)
  collection = client['mydb']['nba_news']
  lines = open('links.tmp', 'r').readlines()

  toggle, title, link = True, None, None
  for l in lines:
    if toggle:
      title = l.strip()
    else:
      link = l.strip()
      
      req = requests.get('{}/{}'.format(head, link))
      page = soup(req.text, 'html.parser')
      section = page.find('section')
      section = '<html><body>{}</body></html>'.format(str(section)) 
      article = soup(section, 'html.parser').find_all('p')

      content = ''.join([ p.text for p in article ])
      print title, link, content

      doc = {
          "title": title,
          "link": '{}/{}'.format(head, link),
          "content": content.replace("\"", "\'")
      }
      collection.insert_one(doc)

    toggle = not toggle

  print collection.count()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Grab tools')
  parser.add_argument('-s', '--step', help='Choose step to run')
  args = parser.parse_args()

  if args.step == '1':
    getLinks()
  elif args.step == '2':
    getNews()
