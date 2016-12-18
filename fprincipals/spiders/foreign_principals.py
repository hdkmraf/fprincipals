# -*- coding: utf-8 -*-
import scrapy


__all__ = ('ForeignPrincipalsSpider',)


class Paginator(object):

    ROWS_PER_PAGE = 100

    p_request = 'APXWGT'
    p_widget_name = 'worksheet'
    p_widget_mod = 'ACTION'
    p_widget_action = 'PAGE'

    p_instance = None
    p_flow_id = None
    p_flow_step_id = None
    x01 = None
    x02 = None

    def __init__(self, p_instance, p_flow_id, p_flow_step_id, x01, x02):
        self._page = 1
        self.p_instance = p_instance
        self.p_flow_id = p_flow_id
        self.p_flow_step_id = p_flow_step_id
        self.x01 = x01
        self.x02 = x02

    def _get_page(self, page):
        action_mod = 'pgR_min_row={min_row}max_rows={rows}rows_fetched={rows}'.format(
            rows=self.ROWS_PER_PAGE,
            min_row=(page - 1) * self.ROWS_PER_PAGE + 1
        )

        return {
            'p_request': self.p_request,
            'p_widget_name': self.p_widget_name,
            'p_widget_mod': self.p_widget_mod,
            'p_widget_action': self.p_widget_action,
            'p_widget_num_return': str(self.ROWS_PER_PAGE),
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
    start_urls = ('https://efile.fara.gov/pls/apex/f?p=171:130:0::NO:RP,130:P130_DATERANGE:N',)
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

            row_url = response.urljoin(row.xpath('td[contains(@headers,"LINK")]/a/@href').extract_first())

            row_data = {
                'url': row_url,
                'country': response.selector.css("th#BREAK_COUNTRY_NAME_1 > span::text").extract_first(),
                'state': row.xpath('td[contains(@headers,"STATE")]/text()').extract_first(),
                'reg_num': row.xpath('td[contains(@headers,"REG_NUMBER")]/text()').extract_first(),
                'address': '\n'.join(row.xpath('td[contains(@headers,"ADDRESS_1")]/text()').extract()),
                'foreign_principal': row.xpath('td[contains(@headers,"FP_NAME")]/text()').extract_first(),
                'date': row.xpath('td[contains(@headers,"REG_DATE")]/text()').extract_first(),
                'registrant': row.xpath('td[contains(@headers,"REGISTRANT_NAME")]/text()').extract_first(),
            }

            yield scrapy.Request(row_data['url'], callback=self.parse_exhibit_url, meta={'row': row_data})

            rows_count += 1

        if (
            # There is a "Next" button on the page
            len(response.selector.css('div#apexir_DATA_PANEL table tr td.pagination > span > a > img[title="Next"]').extract()) == 1
            and rows_count > 0
        ):

            yield scrapy.http.FormRequest(
                self.WWV_FLOW_SHOW_URL,
                formdata=self.paginator.get_next_page(),
                callback=self.parse_page
            )

    def parse_exhibit_url(self, response):
        row_data = response.meta['row']

        row_data['exhibit_url'] = response.selector.css('div#apexir_DATA_PANEL table.apexir_WORKSHEET_DATA').xpath('tr/td[contains(@headers, "DOCLINK")]/a/@href').extract_first()

        yield row_data
