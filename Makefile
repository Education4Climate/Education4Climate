# Macros

YEAR = 2020
ULB_URL="https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes"
UCL_URL="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-2019.html"

# ------------------------------------------------------------------

joujou:
	touch jojo${YEAR}.json

# ------------------------------------------------------------------

test-ulb:
	scrapy shell ${ULB_URL}

test-ucl:
	scrapy shell ${UCL_URL}

# ------------------------------------------------------------------
generate-ucl:
	if [ -f data/ucl_test_${YEAR}.json ]; then rm data/ucl_test_${YEAR}.json; fi
	python3 crawl/ucl.py --output data/ucl_test_${YEAR}.json --year ${YEAR}

generate-ulb:
	if [ -f data/ulb_test_${YEAR}.json ]; then rm data/ulb_test_${YEAR}.json; fi
	python3 crawl/ulb.py --output data/ulb_test_${YEAR}.json --year ${YEAR}

