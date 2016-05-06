#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2014-2016, Sebastian Schulze <info@bascht.com>
#
# This file is part of eurucamp_transcoder
#
# eurucamp_transcoder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# eurucamp_transcoder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with eurucamp_transcoder.  If not, see <http://www.gnu.org/licenses/>.

import bs4
import requests
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
