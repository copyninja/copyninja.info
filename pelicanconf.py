#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = u'Vasudeva Kamath'
SITENAME = u'Random Ramblings'
SITEURL = 'http://localhost:8000'

TIMEZONE = 'Asia/Calcutta'

DEFAULT_LANG = u'en'

# Theme
THEME = os.path.join(os.environ.get('HOME'),
                     'Public/pelican-bootstrap3')

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Display pages in Menu
DISPLAY_PAGES_ON_MENU = True
DEFAULT_PAGINATION = 5
TAG_CLOUD_MAX_ITEMS = 10
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_TAGS_ON_SIDEBAR = True

# License of blog
CC_LICENSE = "CC-BY-NC-SA"

# Github info
GITHUB_USER = "copyninja"

# code highlighting
PYGMENTS_STYLE = "solarizelight"

# Bootstrap theme
BOOTSTRAP_THEME = "flatly"

# Blogroll
LINKS = (('Old Blog Archive', 'http://blog-archive.copyninja.info/'),
         ('Ohloh Profile', 'https://www.ohloh.net/accounts/copyninja'),
         ('Developer Overview (Debian)',
          'http://qa.debian.org/developer.php?login=kamathvasudev@gmail.com'))

# Social widget
SOCIAL = (('twitter', 'https://twitter.com/copyninja_'),
          ('linkedin', 'http://in.linkedin.com/in/kamathvasudev/'),
          ('github', 'https://github.com/copyninja'),
          ('bitbucket', 'https://bitbucket.com/copyninja'))

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# URL generation
ARTICLE_URL = 'blog/{slug}.html'
ARTICLE_SAVE_AS = 'blog/{slug}.html'
PAGE_URL = '{slug}'
PAGE_SAVE_AS = '{slug}.html'
TAG_URL = 'tags/{slug}.html'
TAG_SAVE_AS = 'tags/{slug}.html'
