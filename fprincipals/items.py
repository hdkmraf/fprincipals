# -*- coding: utf-8 -*-
import datetime
import scrapy

from scrapy.loader.processors import TakeFirst, Join, Compose


__all__ = ('ForeignPrincipalItem', 'ForeignPrincipalItemLoader')


def date_input_processor(value):
    """
    :param value: date str
    :return: datetime object
    """

    return datetime.datetime.strptime(value, '%m/%d/%Y')


def date_output_processor(value):
    """
    :param value: datetime object
    :return: date iso string
    """
    return value.isoformat()


class ForeignPrincipalItem(scrapy.Item):
    url = scrapy.Field()
    country = scrapy.Field()
    state = scrapy.Field()
    reg_num = scrapy.Field()
    address = scrapy.Field(
        input_processor=Join(separator='\n')
    )
    foreign_principal = scrapy.Field()
    date = scrapy.Field(
        input_processor=Compose(TakeFirst(), date_input_processor),
        output_processor=Compose(TakeFirst(), date_output_processor)
    )
    registrant = scrapy.Field()
    exhibit_url = scrapy.Field()


class ForeignPrincipalItemLoader(scrapy.loader.ItemLoader):

    default_output_processor = TakeFirst()

    def default_item_class(self):
        return ForeignPrincipalItem()
