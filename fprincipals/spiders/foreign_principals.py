# -*- coding: utf-8 -*-
import scrapy
import urllib


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
    ROWS_PER_PAGE = 15

    def parse(self, response):

        page = 2
        action_mod = 'pgR_min_row={min_row}max_rows={rows}rows_fetched={rows}'.format(
            rows=self.ROWS_PER_PAGE,
            min_row=(page - 1) * self.ROWS_PER_PAGE + 1
        )

        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        for row in response.selector.css('div#apexir_DATA_PANEL table.apexir_WORKSHEET_DATA').xpath('./tr[td]'):

            yield {
                "url": row.xpath('td[contains(@headers,"LINK")]/a/@href').extract_first(),
                "country": response.selector.css("th#BREAK_COUNTRY_NAME_1 > span::text").extract_first(),
                "state": row.xpath('td[contains(@headers,"STATE")]/text()').extract_first(),
                "reg_num": row.xpath('td[contains(@headers,"REG_NUMBER")]/text()').extract_first(),
                "address": '\n'.join(row.xpath('td[contains(@headers,"ADDRESS_1")]/text()').extract()),
                "foreign_principal": row.xpath('td[contains(@headers,"FP_NAME")]/text()').extract_first(),
                "date": row.xpath('td[contains(@headers,"REG_DATE")]/text()').extract_first(),
                "registrant": row.xpath('td[contains(@headers,"REGISTRANT_NAME")]/text()').extract_first(),
                "exhibit_url": ""
            }

        next_request = {
            'p_request': 'APXWGT',
            'p_widget_name': 'worksheet',
            'p_widget_mod': 'ACTION',
            'p_widget_num_return': str(self.ROWS_PER_PAGE),
            'p_widget_action_mod': urllib.quote(action_mod),
            'p_instance': response.selector.css('form#wwvFlowForm input[name=p_instance]::attr(value)').extract_first(),
            'p_flow_id': response.selector.css('form#wwvFlowForm input[name=p_flow_id]::attr(value)').extract_first(),
            'p_flow_step_id': response.selector.css('form#wwvFlowForm input[name=p_flow_step_id]::attr(value)').extract_first(),
            'x01': response.selector.css('input#apexir_WORKSHEET_ID::attr(value)').extract_first(),
            'x02': response.selector.css('input#apexir_REPORT_ID::attr(value)').extract_first()
        }

        yield scrapy.http.FormRequest(self.WWV_FLOW_SHOW_URL, formdata=next_request, callback=self.parse_page)

    def parse_page(self, response):
        pass
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
