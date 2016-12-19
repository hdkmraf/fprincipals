# Scrapping Foreign Principals

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
      "url":"https://efile.fara.gov/pls/apex/f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5945,Exhibit%20AB,AFGHANISTAN",
      "foreign_principal":"Transformation and Continuity, Ajmal Ghani",
      "address":"House #3 MRRD Road\nDarul Aman\nKabul\u00a0\u00a0",
      "date":"2014-05-05T00:00:00",
      "registrant":"Fenton Communications",
      "exhibit_url":"http://www.fara.gov/docs/5945-Exhibit-AB-20140505-10.pdf"
   },
   {  
      "reg_num":"6398",
      "country":"AFGHANISTAN",
      "url":"https://efile.fara.gov/pls/apex/f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:6398,Exhibit%20AB,ANGOLA",
      "foreign_principal":"Movimento de Uniao Nacional (M.U.N) Angola",
      "address":"\u00a0\u00a0",
      "date":"2016-12-01T00:00:00",
      "registrant":"Movimento de Uniao Nacional (M.U.N) Angola",
      "exhibit_url":"http://www.fara.gov/docs/2244-Exhibit-AB-20140331-51.pdf"
   }
]
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
