#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb

import bs4
import requests
import pycurl
from slugify import slugify

def crawl_bucket(url):
    source = requests.get(url)
    keys = bs4.BeautifulSoup(source.content).find_all('key')

    videos = [l.string for l in keys if not l.string.startswith('.')]
    urls   = [{ 'slug': slugify(l.encode('utf-8')), 'url': (url + l)} for l in videos]
    return urls

buckets = {
    'eurucamp': 'http://eurucamp-2014-video.s3.amazonaws.com/',
    'jrubyconf': 'http://jrubyconfeu-2013-video.s3.amazonaws.com/'
}

videos = crawl_bucket(buckets['eurucamp']) + crawl_bucket(buckets['jrubyconf'])

for video in videos:
    print "[%s] => [%s]" % (video['slug'], video['url'])
