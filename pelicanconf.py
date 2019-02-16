#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = u'Vasudeva Kamath'
SITENAME = u'Random Ramblings'
SITESUBTITLE=u'Random thoughts shooting out of volatile mind'
SITEURL = 'http://localhost:8000'

TIMEZONE = 'Asia/Calcutta'

DEFAULT_LANG = u'en'

# Theme
THEME = os.path.join(os.environ.get('HOME'),
                     'Public/pelican-simple/')


# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Display pages in Menu
DISPLAY_PAGES_ON_MENU = True
DEFAULT_PAGINATION = 20
TAG_CLOUD_MAX_ITEMS = 10
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_TAGS_ON_SIDEBAR = True

# License of blog
CC_LICENSE = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported"
SITE_LICENSE = CC_LICENSE

# Github info
GITHUB_USER = "copyninja"

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

STATIC_PATHS = ["images", ]

PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = [
    'pelican_youtube',
    'minification',
    'render_math'
]

# URL generation
ARTICLE_URL = 'blog/{slug}.html'
ARTICLE_SAVE_AS = 'blog/{slug}.html'
PAGE_URL = '{slug}'
PAGE_SAVE_AS = '{slug}.html'
TAG_URL = 'tags/{slug}.html'
TAG_SAVE_AS = 'tags/{slug}.html'

# Save index
#INDEX_SAVE_AS = 'archive.html'

PYGMENTS_RST_OPTIONS = {'linenos': 'none',}
