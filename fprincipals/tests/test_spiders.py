import unittest

from scrapy.selector import Selector

from ..spiders.foreign_principals import Paginator, ForeignPrincipalsSpider


__all__ = ('ForeignPrincipalsPaginationTestCase',)


class FakeResponse(object):

    meta = {}

    def __init__(self, html):
        self.selector = Selector(text=html)


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
