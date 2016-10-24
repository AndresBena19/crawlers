#!/usr/bin/env bash

FILE="/usr/local/zend/apache2/htdocs/jobsity/racc/modules/custom/racc_importer/data/news.json"
SCRAPY="news"

source venv/bin/activate
rm $FILE
scrapy crawl $SCRAPY -o $FILE
cat $FILE | json |  pygmentize -l json
