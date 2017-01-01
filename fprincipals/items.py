# -*- coding: utf-8 -*-
import datetime
import scrapy

from scrapy.loader.processors import TakeFirst, Join, Compose, MapCompose


__all__ = ('ForeignPrincipalItem', 'ForeignPrincipalItemLoader')


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
        input_processor=MapCompose(lambda i: datetime.datetime.strptime(i, '%m/%d/%Y')),
        output_processor=Compose(TakeFirst(), lambda i: i.isoformat())
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
            item[field_name] = self.get_output_value(field_name)

        return item
