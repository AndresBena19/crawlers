#!/usr/bin/env bash

FILE="json/news.json"
SCRAPY="news"

source venv/bin/activate
rm $FILE
scrapy crawl $SCRAPY -o $FILE
cat $FILE | json |  pygmentize -l json
