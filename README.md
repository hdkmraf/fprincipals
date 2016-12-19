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

## Tests

Running unittests:
```bash
python -m unittest fprincipals.tests
```
