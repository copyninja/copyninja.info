#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'https://copyninja.in'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

# Use folders as category
USE_FOLDER_AS_CATEGORY = True

# Metadata
DEFAULT_METADATA = {
    'author': 'Vasudev Kamath',
}

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""
#GITHUB_URL = "https://github.com/copyninja"

SOCIAL = SOCIAL + (('rss', SITEURL + '/' + FEED_ALL_ATOM),)
