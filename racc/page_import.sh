#!/usr/bin/env bash

FILE="/usr/local/zend/apache2/htdocs/jobsity/racc/modules/custom/racc_importer/data/page.json"
SCRAPY="page"

source venv/bin/activate
rm $FILE
scrapy crawl $SCRAPY -o $FILE 2>&1 | tee -a log.log
cat $FILE | json |  pygmentize -l json
