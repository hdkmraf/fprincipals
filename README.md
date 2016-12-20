# Scraping Foreign Principals

Scrap Foreign Principals from [https://www.fara.gov/quick-search.html](https://www.fara.gov/quick-search.html) using Python/Scrapy.

## Installation

```bash
virtualenv .env --no-site-packages -p /usr/local/bin/python2.7
source .env/bin/activate
pip install -r requirements.txt
```

## Run

Storage backend == 'stdout:': 
```bash
scrapy crawl foreign_principals > output.json
```

and `-o` option is available:
```bash
scrapy crawl foreign_principals -o output.json
```

Output example:
```json
[  
   {  
      "reg_num":"5945",
      "country":"AFGHANISTAN",
      "foreign_principal":"Transformation and Continuity, Ajmal Ghani",
      "url":"https://efile.fara.gov/pls/apex/f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5945,Exhibit%20AB,AFGHANISTAN",
      "state":null,
      "address":"House #3 MRRD Road\nDarul Aman\nKabul\u00a0\u00a0",
      "date":"2014-05-05T00:00:00",
      "registrant":"Fenton Communications",
      "exhibit_url":"http://www.fara.gov/docs/5945-Exhibit-AB-20140505-10.pdf"
   },
   {  
      "reg_num":"5965",
      "country":"AFGHANISTAN",
      "foreign_principal":"Government of Aruba",
      "url":"https://efile.fara.gov/pls/apex/f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5965,Exhibit%20AB,ARUBA",
      "state":null,
      "address":"L.G. Smith Blvd. 76\nOranjestad\u00a0\u00a0",
      "date":"2009-12-15T00:00:00",
      "registrant":"Hills Stern & Morley, LLP",
      "exhibit_url":"http://www.fara.gov/docs/5965-Exhibit-AB-20151221-5.pdf"
   }
]
```

Scrapy stats:
```python
{
    'downloader/request_bytes': 258034,
    'downloader/request_count': 520,
    'downloader/request_method_count/GET': 514,
    'downloader/request_method_count/POST': 6,
    'downloader/response_bytes': 9871789,
    'downloader/response_count': 520,
    'downloader/response_status_count/200': 518,
    'downloader/response_status_count/302': 1,
    'downloader/response_status_count/404': 1,
    'finish_reason': 'finished',
    'finish_time': datetime.datetime(2016, 12, 19, 15, 37, 39, 851969),
    'item_scraped_count': 511,
    'log_count/DEBUG': 1032,
    'log_count/INFO': 8,
    'request_depth_max': 7,
    'response_received_count': 519,
    'scheduler/dequeued': 519,
    'scheduler/dequeued/memory': 519,
    'scheduler/enqueued': 519,
    'scheduler/enqueued/memory': 519,
    'start_time': datetime.datetime(2016, 12, 19, 15, 36, 43, 387261)
}
```

## Tests

Running unittests:
```bash
python -m unittest fprincipals.tests
```

Contracts:
```bash
scrapy check foreign_principals
```
