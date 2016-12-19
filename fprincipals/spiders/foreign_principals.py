# -*- coding: utf-8 -*-
import scrapy

from difflib import SequenceMatcher

from ..items import ForeignPrincipalItem


__all__ = ('ForeignPrincipalsSpider',)


class Paginator(object):

    p_request = 'APXWGT'
    p_widget_name = 'worksheet'
    p_widget_mod = 'ACTION'
    p_widget_action = 'PAGE'

    p_instance = None
    p_flow_id = None
    p_flow_step_id = None
    x01 = None
    x02 = None

    _page = 1
    _rows_per_page = 100

    def __init__(self, p_instance, p_flow_id, p_flow_step_id, x01, x02, rows_per_page=100):
        self._page = 1
        self._rows_per_page = rows_per_page
        self.p_instance = p_instance
        self.p_flow_id = p_flow_id
        self.p_flow_step_id = p_flow_step_id
        self.x01 = x01
        self.x02 = x02

    def _get_page(self, page):
        action_mod = 'pgR_min_row={min_row}max_rows={rows}rows_fetched={rows}'.format(
            rows=self._rows_per_page,
            min_row=(page - 1) * self._rows_per_page + 1
        )

        return {
            'p_request': self.p_request,
            'p_widget_name': self.p_widget_name,
            'p_widget_mod': self.p_widget_mod,
            'p_widget_action': self.p_widget_action,
            'p_widget_num_return': str(self._rows_per_page),
            'p_widget_action_mod': action_mod,
            'p_instance': self.p_instance,
            'p_flow_id': self.p_flow_id,
            'p_flow_step_id': self.p_flow_step_id,
            'x01': self.x01,
            'x02': self.x02
        }

    def get_first_page(self):
        self._page = 1

        return self._get_page(page=self._page)

    def get_next_page(self):
        self._page += 1

        return self._get_page(page=self._page)


class ForeignPrincipalsSpider(scrapy.Spider):
    """
    Extract foreign principals from https://www.fara.gov/quick-search.html
    (Click "Active Foreign Principals")
    """

    name = 'foreign_principals'

    # https://www.fara.gov/quick-search.html -> "Active Foreign Principals" link
    start_urls = ('https://efile.fara.gov/pls/apex/f?p=171:130:::NO:RP,130:P130_DATERANGE:N',)
    allowed_domains = ('efile.fara.gov',)

    WWV_FLOW_SHOW_URL = 'https://efile.fara.gov/pls/apex/wwv_flow.show'
    PLS_APEX_URL = 'https://efile.fara.gov/pls/apex/'
    ROWS_PER_PAGE = 15

    paginator = None

    def parse(self, response):

        self.paginator = Paginator(
            p_instance=response.selector.css('form#wwvFlowForm input[name=p_instance]::attr(value)').extract_first(),
            p_flow_id=response.selector.css('form#wwvFlowForm input[name=p_flow_id]::attr(value)').extract_first(),
            p_flow_step_id=response.selector.css('form#wwvFlowForm input[name=p_flow_step_id]::attr(value)').extract_first(),
            x01=response.selector.css('input#apexir_WORKSHEET_ID::attr(value)').extract_first(),
            x02=response.selector.css('input#apexir_REPORT_ID::attr(value)').extract_first()
        )

        yield scrapy.http.FormRequest(
            self.WWV_FLOW_SHOW_URL,
            formdata=self.paginator.get_first_page(),
            callback=self.parse_page
        )

    def parse_page(self, response):

        rows_count = 0

        for row in response.selector.css('div#apexir_DATA_PANEL table.apexir_WORKSHEET_DATA').xpath('./tr[td]'):

            # remove "0" in "...171:200:0::..."
            relative_url_parts = row.xpath('td[contains(@headers,"LINK")]/a/@href').extract_first().split(':')
            row_url = response.urljoin(':'.join(relative_url_parts[:2] + [''] + relative_url_parts[3:]))

            row_item = ForeignPrincipalItem(
                url=row_url,
                country=response.selector.css("th#BREAK_COUNTRY_NAME_1 > span::text").extract_first(),
                state=row.xpath('td[contains(@headers,"STATE")]/text()').extract_first(),
                reg_num=row.xpath('td[contains(@headers,"REG_NUMBER")]/text()').extract_first(),
                address='\n'.join(row.xpath('td[contains(@headers,"ADDRESS_1")]/text()').extract()),
                foreign_principal=row.xpath('td[contains(@headers,"FP_NAME")]/text()').extract_first(),
                date=row.xpath('td[contains(@headers,"REG_DATE")]/text()').extract_first(),
                registrant=row.xpath('td[contains(@headers,"REGISTRANT_NAME")]/text()').extract_first(),
            )

            yield scrapy.Request(row_url, callback=self.parse_exhibit_url, meta={'row': row_item}, dont_filter=True)

            rows_count += 1

        if (
            # There is a "Next" button on the page
            len(response.selector.css('div#apexir_DATA_PANEL table tr td.pagination > span > a > img[title="Next"]').extract()) == 1
            and rows_count > 0
            and False
        ):

            yield scrapy.http.FormRequest(
                self.WWV_FLOW_SHOW_URL,
                formdata=self.paginator.get_next_page(),
                callback=self.parse_page
            )

    def parse_exhibit_url(self, response):
        row_item = response.meta['row']

        found = []

        for document in response.selector.css('div#apexir_DATA_PANEL table.apexir_WORKSHEET_DATA').xpath('tr/td[contains(@headers, "DOCLINK")]/a'):

            found.append((
                SequenceMatcher(
                    None,
                    row_item['foreign_principal'].strip().lower(),
                    document.xpath('./span/text()').extract_first().strip().lower()
                ).ratio() * 1000 - len(found),  # similarity (0..1000) - position
                document.xpath('@href').extract_first()
            ))

        if found:
            # find the most relevant and recent url
            found.sort(key=lambda i: i[0], reverse=True)
            row_item['exhibit_url'] = found[0][1]

        yield row_item
