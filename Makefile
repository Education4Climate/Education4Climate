# Macros

YEAR = 2020
ULB_URL="https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes"
UCL_URL="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-${YEAR}.html"
UANTWERP_URL="https://www.uantwerpen.be/en/study/education-and-training/"

# ------------------------------------------------------------------

test-ulb:
	scrapy shell ${ULB_URL}

test-ucl:
	scrapy shell ${UCL_URL}

test-uantwerp:
	scrapy shell ${UANTWERP_URL}

# ------------------------------------------------------------------
generate-ucl:
	if [ -f data/ucl_test_${YEAR}.json ]; then rm data/ucl_test_${YEAR}.json; fi
	python3 crawl/ucl.py --output data/ucl_test_${YEAR}.json --year ${YEAR}

generate-ulb:
	if [ -f data/ulb_test_${YEAR}.json ]; then rm data/ulb_test_${YEAR}.json; fi
	python3 crawl/ulb.py --output data/ulb_test_${YEAR}.json --year ${YEAR}

generate-uantwerp:
	if [ -f data/uantwerp_${YEAR}.json ]; then rm data/uantwerp_${YEAR}.json; fi
	python3 crawl/uantwerp.py --output data/uantwerp_${YEAR}.json --year ${YEAR}
