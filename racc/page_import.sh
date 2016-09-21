#!/usr/bin/env bash

FILE="json/page.json"
SCRAPY="page"

source venv/bin/activate
rm $FILE
scrapy crawl $SCRAPY -o $FILE
cat $FILE | json |  pygmentize -l json
