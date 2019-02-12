#!/usr/bin/env python

SITENAME = 'Paweł Fertyk'
SITEURL = 'https://pfertyk.me'
SITE_DESCTIPTION = "Paweł Fertyk's blog on programming"

AUTHOR_NAME = 'Paweł Fertyk'

PATH = 'content'

TIMEZONE = 'Europe/Warsaw'
DEFAULT_LANG = 'en'

DELETE_OUTPUT_DIRECTORY = True
RELATIVE_URLS = True

THEME = 'my-theme'

PAGE_URL = '/{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

ARTICLE_URL = '/{date:%Y}/{date:%m}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{slug}/index.html'

CATEGORY_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
TAGS_URL = '/tags/'
TAGS_SAVE_AS = 'tags/index.html'
TAG_URL = '/tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'

FEED_ALL_RSS = 'feeds/all.rss.xml'
FEED_ATOM = None
TAG_FEED_ATOM = 'feeds/%s.atom.xml'
TAG_FEED_RSS = 'feeds/%s.rss.xml'
TRANSLATION_FEED_ATOM = None
CATEGORY_FEED_ATOM = None
