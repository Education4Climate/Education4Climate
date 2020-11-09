# Macros

YEAR = 2020
ULB_URL="https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes"
UCL_URL="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-${YEAR}.html"
UANTWERP_URL="https://www.uantwerpen.be/en/study/education-and-training/"
UGENT_URL="https://studiegids.ugent.be/${YEAR}/EN/FACULTY/faculteiten.html"
KULEUVEN_URL = "https://onderwijsaanbod.kuleuven.be/opleidingen/e/index.htm"

# ------------------------------------------------------------------

test-ucl:
	scrapy shell ${UCL_URL}

test-ulb:
	scrapy shell ${ULB_URL}

test-uantwerp:
	scrapy shell ${UANTWERP_URL}

test-ugent:
	scrapy shell ${UGENT_URL}

test-kuleuven:
	scrapy shell ${KULEUVEN_URL}

# ------------------------------------------------------------------

generate-ucl:
	if [ -f data/ucl_${YEAR}.json ]; then rm data/ucl_${YEAR}.json; fi
	python3 crawl/ucl.py --output data/crawling-results/ucl_${YEAR}.json --year ${YEAR}

generate-ulb:
	if [ -f data/ulb_${YEAR}.json ]; then rm data/ulb_${YEAR}.json; fi
	python3 crawl/ulb.py --output data/crawling-results/ulb_${YEAR}.json --year ${YEAR}

generate-uantwerp:
	if [ -f data/uantwerp_${YEAR}.json ]; then rm data/uantwerp_${YEAR}.json; fi
	python3 crawl/uantwerp.py --output data/crawling-results/uantwerp_${YEAR}.json --year ${YEAR}

generate-ugent:
	if [ -f data/ugent_${YEAR}.json ]; then rm data/ugent_${YEAR}.json; fi
	python3 crawl/ugent_webdriver.py --output data/crawling-results/ugent_${YEAR}.json --year ${YEAR}

generate-kuleuven:
	if [ -f data/kuleuven_${YEAR}.json ]; then rm data/kuleuven_${YEAR}.json; fi
	python3 crawl/kuleuven.py --output data/crawling-results/kuleuven_${YEAR}.json --year ${YEAR}

#--------------------------------------------------------------------

score-ucl:
	python process/score_script.py --input data/crawling-results/ucl_${YEAR}.json --output data/ucl_scoring_${YEAR}.csv --key shortname --field content

score-ulb:
	python process/score_script.py --input data/crawling-results/ulb_${YEAR}.json --output data/ulb_scoring_${YEAR}.csv --key shortname --field content

score-uantwerp:
	python process/score_script.py --input data/crawling-results/uantwerp_${YEAR}.json --output data/uantwerp_scoring_${YEAR}.csv --key shortname --field content

score-ugent:
	python process/score_script.py --input data/crawling-results/ugent_${YEAR}.json --output data/ugent_scoring_${YEAR}.csv --key shortname --field content

score-kuleuven:
	python process/score_script.py --input data/crawling-results/kuleuven_${YEAR}.json --output data/kuleuven_scoring_${YEAR}.csv --key shortname --field content