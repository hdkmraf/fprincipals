import unittest

from six.moves.urllib.parse import urljoin

import scrapy

from ..spiders.foreign_principals import Paginator, ForeignPrincipalsSpider
from .utils import rel


__all__ = ('ForeignPrincipalsPaginationTestCase',)


class FakeResponse(object):

    meta = {}
    url = ""

    def urljoin(self, url):
        return urljoin(self.url, url)

    def __init__(self, html):
        self.selector = scrapy.Selector(text=html)


class ForeignPrincipalsPaginationTestCase(unittest.TestCase):

    def test_paginator(self):
        paginator = Paginator(
            p_instance='7401450318019',
            p_flow_id='171',
            p_flow_step_id='130',
            x01='80340213897823017',
            x02='80341508791823021',
            rows_per_page=15
        )

        self.assertEqual(
            paginator.get_first_page(),
            {
                'p_widget_mod': 'ACTION',
                'p_instance': '7401450318019',
                'p_widget_num_return': '15',
                'p_widget_name': 'worksheet',
                'p_flow_step_id': '130',
                'p_widget_action': 'PAGE',
                'p_widget_action_mod': 'pgR_min_row=1max_rows=15rows_fetched=15',
                'p_flow_id': '171',
                'p_request': 'APXWGT',
                'x02': '80341508791823021',
                'x01': '80340213897823017'
            })

        self.assertEqual(
            paginator.get_next_page(),
            {
                'p_widget_mod': 'ACTION',
                'p_instance': '7401450318019',
                'p_widget_num_return': '15',
                'p_widget_name': 'worksheet',
                'p_flow_step_id': '130',
                'p_widget_action': 'PAGE',
                'p_widget_action_mod': 'pgR_min_row=16max_rows=15rows_fetched=15',
                'p_flow_id': '171',
                'p_request': 'APXWGT',
                'x02': '80341508791823021',
                'x01': '80340213897823017'
            })

        # rows per page

        paginator = Paginator(
            p_instance='7401450318019',
            p_flow_id='171',
            p_flow_step_id='130',
            x01='80340213897823017',
            x02='80341508791823021',
            rows_per_page=100
        )

        page = paginator.get_first_page()
        self.assertEqual(page['p_widget_num_return'], '100')
        self.assertEqual(page['p_widget_action_mod'], 'pgR_min_row=1max_rows=100rows_fetched=100')

    def test_exhibit_url(self):
        """
        Choose the most relevant and then the most recent file.
        """

        page_html = """<html><body><div id="apexir_DATA_PANEL">
<table summary="">
<tr><td><table summary="" cellpadding="0" cellspacing="0" border="0" class="apexir_WORKSHEET_DATA" id="90738522271518332">
<tr><th id="DATE_STAMPED"><div id="apexir_DATE_STAMPED" onclick="gReport.controls.widget(this.id)" style="text-align:left;">Date Stamped<img src="/i/arrow_down_gray_light.gif" width="13" height="12"></div></th><th id="DOCLINK"><div id="apexir_DOCLINK" onclick="gReport.controls.widget(this.id)" style="text-align:left;">View Document</div></th><th id="REGISTRATION_NUMBER"><div id="apexir_REGISTRATION_NUMBER" onclick="gReport.controls.widget(this.id)" style="text-align:right;">Registration #</div></th><th id="REGISTRANT_NAME"><div id="apexir_REGISTRANT_NAME" onclick="gReport.controls.widget(this.id)" style="text-align:left;">Registrant Name</div></th><th id="DOCUMENT_TYPE"><div id="apexir_DOCUMENT_TYPE" onclick="gReport.controls.widget(this.id)" style="text-align:center;">Document Type</div></th></tr>

<tr class="even"><td align="left" headers="DATE_STAMPED">01/20/2015</td><td align="left" headers="DOCLINK"><a target="5839-Exhibit-AB-20150120-29" href="http://www.fara.gov/file1.pdf"><span style="color:blue">Title 1</span></a></td><td align="right" headers="REGISTRATION_NUMBER">5839</td><td align="left" headers="REGISTRANT_NAME">Sorini, Samet &amp; Associates, LLC</td><td align="left" headers="DOCUMENT_TYPE">Exhibit AB</td></tr>
<tr class="odd"><td align="left" headers="DATE_STAMPED">05/26/2011</td><td align="left" headers="DOCLINK"><a target="5839-Exhibit-AB-20110526-21" href="http://www.fara.gov/file2.pdf"><span style="color:blue">Title 2</span></a></td><td align="right" headers="REGISTRATION_NUMBER">5839</td><td align="left" headers="REGISTRANT_NAME">Sorini, Samet &amp; Associates, LLC</td><td align="left" headers="DOCUMENT_TYPE">Exhibit AB</td></tr>
<tr class="odd"><td align="left" headers="DATE_STAMPED">05/26/2010</td><td align="left" headers="DOCLINK"><a target="5839-Exhibit-AB-20110526-21" href="http://www.fara.gov/file3.pdf"><span style="color:blue">Title 2</span></a></td><td align="right" headers="REGISTRATION_NUMBER">5839</td><td align="left" headers="REGISTRANT_NAME">Sorini, Samet &amp; Associates, LLC</td><td align="left" headers="DOCUMENT_TYPE">Exhibit AB</td></tr>

</table>
</td></tr><tr class="fielddatasmall" align="left"><td>
</td></tr>
<tr><td colspan="6" class="pagination" align="right"><span class="fielddata"> 1 - 2 of 2 </span></td></tr>
</table>
</div></body></html>"""

        RIGHT_CHOICES = {
            "Title 1": 'http://www.fara.gov/file1.pdf',
            "Tile 1": 'http://www.fara.gov/file1.pdf',
            "Title 2": 'http://www.fara.gov/file2.pdf',
            "tile 2": 'http://www.fara.gov/file2.pdf'
        }

        spider = ForeignPrincipalsSpider()
        response = FakeResponse(html=page_html)

        for title, url in RIGHT_CHOICES.iteritems():

            response.meta['row'] = {
                'foreign_principal': title
            }

            for data in spider.parse_exhibit_url(response=response):
                self.assertEqual(data['exhibit_url'], url)

    def test_parse_page(self):
        """
        Check right data was chosen.
        Check pagination stop if there is no Next button.
        """

        with open(rel('data/foreign_principals_table.html'), 'r') as f:
           page_html = f.read()

        response = FakeResponse(html=page_html)

        spider = ForeignPrincipalsSpider()
        spider.paginator = Paginator(p_instance="", p_flow_id="", p_flow_step_id="", x01="", x02="")

        data_requests = []
        next_page_requests = []

        for data in spider.parse_page(response):

            if isinstance(data, scrapy.http.Request):
                if data.method == 'GET':
                    data_requests.append(data)
                elif data.method == 'POST':
                    next_page_requests.append(data)

        self.assertEqual(len(data_requests), 2)
        self.assertEqual(len(next_page_requests), 1)

        self.assertEqual(
            data_requests[0].meta['row'],
            {
                'reg_num': u'6065',
                'state': u'DC',
                'date': u'07/28/2013',
                'address': [u'1319 18th Street, NW', u'Washington\xa0\xa020036'],
                'url': u'f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:6065,Exhibit%20AB,AZERBAIJAN',
                'country': u'AZERBAIJAN',
                'foreign_principal': u'SOCAR USA, subsidiary of State Oil Company of Azerbaijan Republic (SOCAR)',
                'registrant': u'Roberti + White, LLC'
            }
        )

        # test stop pagination

        last_page_html = page_html.replace('Next', '')

        response = FakeResponse(html=last_page_html)

        next_page_requests = []

        for data in spider.parse_page(response):

            if isinstance(data, scrapy.http.Request):
                if data.method == 'POST':
                    next_page_requests.append(data)

        self.assertFalse(next_page_requests)
