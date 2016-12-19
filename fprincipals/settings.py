# -*- coding: utf-8 -*-

# Scrapy settings for fprincipals project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'fprincipals'

SPIDER_MODULES = ['fprincipals.spiders']
NEWSPIDER_MODULE = 'fprincipals.spiders'

# Feed

FEED_URI = 'stdout:'
FEED_FORMAT = 'json'

# engine

ROBOTSTXT_OBEY = True
COOKIES_ENABLED = True

DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html',
   'Accept-Language': 'en',
}

# TODO: set this settings

# USER_AGENT = 'fprincipals (+http://www.yourdomain.com)'
# CONCURRENT_REQUESTS = 32  # default: 16
# DOWNLOAD_DELAY = 3  # default: 0, see http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# TELNETCONSOLE_ENABLED = False
