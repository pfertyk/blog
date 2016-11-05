#!/usr/bin/env python
from urllib.parse import quote

SITENAME = 'pfertyk'
SITEURL = 'http://pfertyk.me'
SITE_DESCTIPTION = "Paweł Fertyk's blog on programming"

AUTHOR_NAME = 'Paweł Fertyk'
TWITTER_USERNAME = 'pfertyk'

PATH = 'content'

TIMEZONE = 'Europe/Warsaw'
DEFAULT_LANG = 'en'

DELETE_OUTPUT_DIRECTORY = True
RELATIVE_URLS = False

THEME = 'my-theme'

TEMPLATE_PAGES = {'about.html': 'about/index.html'}

ARTICLE_URL = '{date:%Y}/{date:%m}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{slug}/index.html'

CATEGORY_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
TAGS_SAVE_AS = ''
TAG_SAVE_AS = ''

FEED_ALL_RSS = 'feeds/all.rss.xml'
FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
CATEGORY_FEED_ATOM = None


def twitter_link(article):
    return 'https://twitter.com/intent/tweet?text={}&url={}&via={}'.format(
        quote(article.title),
        quote(SITEURL + '/' + article.url),
        TWITTER_USERNAME
    )


JINJA_FILTERS = {'twitter_link': twitter_link}
