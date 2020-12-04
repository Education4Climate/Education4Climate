# Macros

YEAR = 2020

CRAWLER_FOLDER = src/crawl
SCORING_FOLDER = src/score

CRAWLING_OUTPUT_FOLDER = data/crawling-output
SCORING_OUTPUT_FOLDER = data/scoring-output


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

crawl-ucl:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/ucl_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/ucl_${YEAR}.json; fi
	python3 ${CRAWLER_FOLDER}/ucl.py --output ${CRAWLING_OUTPUT_FOLDER}/ucl_${YEAR}.json --year ${YEAR}

crawl-ulb:
	if [ -f data/ulb_${YEAR}.json ]; then rm data/ulb_${YEAR}.json; fi
	python3 ${CRAWLER_FOLDER}/ulb.py --output ${CRAWLING_OUTPUT_FOLDER}/ulb_${YEAR}.json --year ${YEAR}

crawl-uantwerp:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/uantwerp_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/uantwerp_${YEAR}.json; fi
	python3 ${CRAWLER_FOLDER}//uantwerp.py --output ${CRAWLING_OUTPUT_FOLDER}/uantwerp_${YEAR}.json --year ${YEAR}

crawl-ugent:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/ugent_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/ugent_${YEAR}.json; fi
	python3 ${CRAWLER_FOLDER}/ugent_webdriver.py --output ${CRAWLING_OUTPUT_FOLDER}/ugent_${YEAR}.json --year ${YEAR}

crawl-kuleuven:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/kuleuven_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/kuleuven_${YEAR}.json; fi
	python3 ${CRAWLER_FOLDER}/kuleuven.py --output ${CRAWLING_OUTPUT_FOLDER}/kuleuven_${YEAR}.json --year ${YEAR}

#--------------------------------------------------------------------

score-ucl:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/ucl_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/ucl_scoring_${YEAR}.csv

score-ulb:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/ulb_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/ulb_scoring_${YEAR}.csv

score-uantwerp:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/uantwerp_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/uantwerp_scoring_${YEAR}.csv

score-ugent:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/ugent_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/ugent_scoring_${YEAR}.csv

score-kuleuven:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/kuleuven_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/kuleuven_scoring_${YEAR}.csv


# Other useful commands ---------------------------------------------------

download_spacy_en:
	python -m spacy download en