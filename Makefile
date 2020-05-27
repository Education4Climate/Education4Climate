# Macros

ULB_URL=https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes
UCL_URL=https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes

generate-ulb:
    python3 crawl/ulb.py --output data/ulb_test.json

test-ulb:
    scrapy shell https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes

generate-ucl:
    python3 crawl/ucl.py --output data/ucl_test.json

test-ucl:
    scrapy shell ${UCL_URL}
