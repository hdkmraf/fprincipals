# -*- coding: utf-8 -*-
import datetime
import scrapy

from scrapy.loader.processors import TakeFirst, Join, Compose


__all__ = ('ForeignPrincipalItem', 'ForeignPrincipalItemLoader')


def date_decode_processor(value):
    """
    :param value: date str
    :return: datetime object
    """

    return datetime.datetime.strptime(value, '%m/%d/%Y')


def date_encode_processor(value):
    """
    :param value: datetime object
    :return: date iso string
    """
    return value.isoformat()


class IdentityOrNone(object):

    def __call__(self, values):
        if values:
            return values
        return [None]


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
        input_processor=Compose(TakeFirst(), date_decode_processor),
        output_processor=Compose(TakeFirst(), date_encode_processor)
    )
    registrant = scrapy.Field()
    exhibit_url = scrapy.Field()


class ForeignPrincipalItemLoader(scrapy.loader.ItemLoader):

    default_input_processor = IdentityOrNone()
    default_output_processor = TakeFirst()
    default_item_class = ForeignPrincipalItem

    def load_item(self):
        """
        Overriding to enable null values in output.
        """
        item = self.item
        for field_name in tuple(self._values):
            value = self.get_output_value(field_name)
            item[field_name] = value

        return item
