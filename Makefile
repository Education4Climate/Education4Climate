# Macros

YEAR = 2020
ULB_URL="https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes"
UCL_URL="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-${YEAR}.html"
UANTWERP_URL="https://www.uantwerpen.be/en/study/education-and-training/"
UGENT_URL="https://studiegids.ugent.be/${YEAR}/EN/FACULTY/faculteiten.html"
KULEUVEN_URL = "https://onderwijsaanbod.kuleuven.be/opleidingen/e/index.htm"

# ------------------------------------------------------------------

test-ulb:
	scrapy shell ${ULB_URL}

test-ucl:
	scrapy shell ${UCL_URL}

test-uantwerp:
	scrapy shell ${UANTWERP_URL}

test-ugent:
	scrapy shell ${UGENT_URL}

test-kuleuven:
	scrapy shell ${KULEUVEN_URL}

# ------------------------------------------------------------------
generate-ucl:
	if [ -f data/ucl_test_${YEAR}.json ]; then rm data/ucl_test_${YEAR}.json; fi
	python3 crawl/ucl.py --output data/crawling-results/ucl_test_${YEAR}.json --year ${YEAR}

generate-ulb:
	if [ -f data/ulb_test_${YEAR}.json ]; then rm data/ulb_test_${YEAR}.json; fi
	python3 crawl/ulb.py --output data/crawling-results/ulb_test_${YEAR}.json --year ${YEAR}

generate-uantwerp:
	if [ -f data/uantwerp_${YEAR}.json ]; then rm data/uantwerp_${YEAR}.json; fi
	python3 crawl/uantwerp.py --output data/crawling-results/uantwerp_${YEAR}.json --year ${YEAR}

generate-ugent:
	if [ -f data/ugent_${YEAR}.json ]; then rm data/ugent_${YEAR}.json; fi
	python3 crawl/ugent.py --output data/crawling-results/ugent_${YEAR}.json --year ${YEAR}

generate-kuleuven:
	if [ -f data/kuleuven_${YEAR}.json ]; then rm data/kuleuven_${YEAR}.json; fi
	python3 crawl/kuleuven.py --output data/crawling-results/kuleuven_${YEAR}.json --year ${YEAR}