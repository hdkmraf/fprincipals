# -*- coding: utf-8 -*-
import scrapy


class ForeignPrincipalsSpider(scrapy.Spider):
    """
    Extract foreign principals from https://www.fara.gov/quick-search.html
    (Click "Active Foreign Principals")
    """

    name = 'foreign_principals'
    start_urls = ('https://efile.fara.gov/pls/apex/f?p=171:130:0::NO:RP,130:P130_DATERANGE:N',)
    allowed_domains = ('nanvel.name',)

    def parse(self, response):
        pass
