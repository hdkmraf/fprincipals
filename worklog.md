Plan:

- analyze the data source (page structure, api, etc.)
- create a repository
- check out scrapy
- update the plan

---

Plan:

- basic scraper, pagination
- try debug tools
- find all the required data on the page
- email questions
- plan update

```text
https://www.fara.gov/quick-search.html -> "Active Foreign Principals" link
https://efile.fara.gov/pls/apex/f?p=171:130:0::NO:RP,130:P130_DATERANGE:N
There is a form on the page.

Pagination:
javascript:gReport.navigate.paginate('pgR_min_row=16max_rows=15rows_fetched=15')
https://efile.fara.gov/i/libraries/apex/minified/widget.interactiveReport.min.js?v=4.2.5.00.08

2rd page: pgR_min_row=16max_rows=15rows_fetched=15
3nd page: pgR_min_row=31max_rows=15rows_fetched=15
```
Trying to figure out pagination logic out of the js...

On next click:
```
POST:https://efile.fara.gov/pls/apex/wwv_flow.show
p_request=APXWGT& (looks like a const)
p_instance=15673377578171& (wwv_flow form)
p_flow_id=171& (wwv_flow form)
p_flow_step_id=130& (wwv_flow form)
p_widget_num_return=15& ("pgR_min_row=16max_rows=15rows_fetched=15".split("max_rows=")[1].split("rows_fetched")[0])
p_widget_name=worksheet& (looks like const)
p_widget_mod=ACTION& (looks like const for the request)
p_widget_action=PAGE& (looks like const for the request)
p_widget_action_mod=pgR_min_row%3D16max_rows%3D15rows_fetched%3D15& (pgR_min_row=16max_rows=15rows_fetched=15)
x01=80340213897823017& ($v("apexir_WORKSHEET_ID"), div#apexir_WORKSHEET -> input#apexir_WORKSHEET_ID)
x02=80341508791823021 (that.report_id or "0", div#apexir_WORKSHEET -> input#apexir_REPORT_ID)
```

`https://efile.fara.gov/pls/apex/wwv_flow.show` response a bit different from `https://efile.fara.gov/pls/apex/f`, figuring out how to parse it ...
Looks like nothing changes from page to page except `pgR_min_row=16max_rows=15rows_fetched=15`.

Got "The requested URL was rejected. Please consult with your administrator." for the second page. Will get back to this later.
Next: find all the necessary data in the rows.

Fields:
```text
"url": "https://efile.fara.gov/pls/apex/f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:2310,Exhibit%20AB,BAHAMAS",
"country": "BAHAMAS",
"state": null,
"reg_num": "2310",
"address": "Nassau",
"foreign_principal": "Bahamas Ministry of Tourism",
"date" :ISODate("1972-01-27T00:00:00Z"),
"registrant": "Bahamas Tourist Office",
"exhibit_url": "http://www.fara.gov/docs/2310-Exhibit-AB-19720101-DBBMB702.pdf"
```

Row example `//*[@id="apexir_DATA_PANEL"]/table/tbody/tr[1]/td/table/tbody/tr[3]`:
```html
<tr class="even">
    <td headers="LINK BREAK_COUNTRY_NAME_1"><a href="f?p=171:200:0::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5945,Exhibit%20AB,AFGHANISTAN"><img src="/i/view.gif" alt="View Documents"></a></td>
    <td align="left" headers="FP_NAME BREAK_COUNTRY_NAME_1">Transformation and Continuity, Ajmal Ghani</td>
    <td align="left" headers="FP_REG_DATE BREAK_COUNTRY_NAME_1">05/05/2014</td>
    <td align="left" headers="ADDRESS_1 BREAK_COUNTRY_NAME_1">House #3 MRRD Road<br>Darul Aman<br>Kabul&nbsp;&nbsp;</td>
    <td align="left" headers="STATE BREAK_COUNTRY_NAME_1"></td>
    <td align="left" headers="REGISTRANT_NAME BREAK_COUNTRY_NAME_1">Fenton Communications</td>
    <td align="center" headers="REG_NUMBER BREAK_COUNTRY_NAME_1">5945</td>
    <td align="left" headers="REG_DATE BREAK_COUNTRY_NAME_1">06/26/2009</td>
</tr>
```

```text
response.selector.css('div#apexir_DATA_PANEL table.apexir_WORKSHEET_DATA').xpath('./tr[td]')

row.xpath('td[contains(@headers,"LINK")]/a/@href').extract_first()
u'f?p=171:200:0::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5945,Exhibit%20AB,AFGHANISTAN'

row.xpath('td[contains(@headers,"LINK")]/@headers').extract_first().split(' ')[1]
u'BREAK_COUNTRY_NAME_1'

row.xpath('td[contains(@headers,"STATE")]/text()').extract_first()
u''

response.selector.css("th#BREAK_COUNTRY_NAME_1 > span::text").extract_first()
u'AFGHANISTAN'

row.xpath('td[contains(@headers,"REG_NUMBER")]/text()').extract_first()
u'5945'

'\n'.join(row.xpath('td[contains(@headers,"ADDRESS_1")]/text()').extract())
u'House #3 MRRD Road\nDarul Aman\nKabul\xa0\xa0'

row.xpath('td[contains(@headers,"FP_NAME")]/text()').extract_first()
u'Transformation and Continuity, Ajmal Ghani'

row.xpath('td[contains(@headers,"REG_DATE")]/text()').extract_first()
u'05/05/2014'

row.xpath('td[contains(@headers,"REGISTRANT_NAME")]/text()').extract_first()
u'Fenton Communications'

exhibit_url: click on "view" in a row left side. 
```

---

Plan:

- extract exhibit url
- fix pagination
- create an Item
- email questions
- plan update

Fixed url, added `/pls/apex/`.

I believe it's possible to have a few documents on a Documents page, so I'll be choosing the latest one (ordered by Date Stamped, desc).

```python
# https://efile.fara.gov/pls/apex/f?p=171:200:0::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:6065,Exhibit%20AB,AFGHANISTAN
response.selector.css('div#apexir_DATA_PANEL table.apexir_WORKSHEET_DATA').xpath('tr/td[contains(@headers, "DOCLINK")]/a/@href').extract_first()
```

The second page request body and headers:
```text
In [2]: request.body
Out[2]: 'p_flow_id=171&p_widget_mod=ACTION&x01=80340213897823017&p_instance=14535582550857&p_request=APXWGT&p_widget_num_return=15&x02=80341508791823021&p_widget_name=worksheet&p_flow_step_id=130&p_widget_action_mod=pgR_min_row%253D16max_rows%253D15rows_fetched%253D15'

In [3]: request.headers
Out[3]: 
{'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
 'Accept-Encoding': 'gzip,deflate',
 'Accept-Language': 'en',
 'Content-Type': 'application/x-www-form-urlencoded',
 'Cookie': 'ORA_WWV_APP_171=ORA_WWV-mJaRpb2yA8lyG5BwQ37PgLSY; TS013766ce=016889935cbd588b97d5142b582e1c5dd9f3cbd2aed66b6a6669eaeacef4f96c512f2463d2d25297ddbb7961aa6989558591328925',
 'Referer': 'https://efile.fara.gov/pls/apex/f?p=171:130:0::NO:RP,130:P130_DATERANGE:N',
 'User-Agent': 'Scrapy/1.2.2 (+http://scrapy.org)'}

In [4]: response.body
Out[4]: '<html><head><title>Request Rejected</title></head><body>The requested URL was rejected. Please consult with your administrator.<br><br>Your support ID is: 1132525161098826485</body></html>'

In [5]: request.url
Out[5]: 'https://efile.fara.gov/pls/apex/wwv_flow.show'
```
Comparing to what I have in browser ...

Found differences:
```
p_instance=14535582550857
p_instance=7401450318019
p_widget_action_mod=pgR_min_row%253D16max_rows%253D15rows_fetched%253D15
p_widget_action_mod=pgR_min_row%3D16max_rows%3D15rows_fetched%3D15
<empty>
p_widget_action=PAGE
```

Pagination stop:
```text
response.selector.css('div#apexir_DATA_PANEL table tr td.pagination > span > a > img[title="Next"]').extract()
Out[30]: [u'<img src="/i/jtfunexe.gif" title="Next" alt="Next" align="absmiddle">']

or page is empty.
```

Now scraper returns 483 records instead of 511.

5x100 and 11 rows was processed, maybe duplicates?

---

Future:

- unittest scrapers (contracts)?
- write a basic scraper, get necessary data
- how to run
- declare an Item
- use ItemPipeline to save data (requires activation)?
- export (use stdout?) or just use -o, create an egg?
- review settings, what I need to modify?
- do I need to save state?
- compare output data to what I see in the browser
- address line and date format
- add domain for url
- pep8 and check for memory leaks

Questions:

- address lines
- date format
- if many documents - choose the latest (https://efile.fara.gov/pls/apex/f?p=171:200:0::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:1032,Exhibit%20AB,AUSTRALIA)
