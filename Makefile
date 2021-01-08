# Macros

YEAR = 2020

CRAWLER_FOLDER = src/crawl/unicrawl/spiders
SCORING_FOLDER = src/score

CRAWLING_OUTPUT_FOLDER = data/crawling-output
SCORING_OUTPUT_FOLDER = data/scoring-output


ULB_URL="https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes"
UCL_URL="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-${YEAR}.html"
UANTWERP_URL="https://www.uantwerpen.be/en/study/education-and-training/"
UGENT_URL="https://studiegids.ugent.be/${YEAR}/EN/FACULTY/faculteiten.html"
KULEUVEN_URL = "https://onderwijsaanbod.kuleuven.be/opleidingen/e/index.htm"
UMONS_URL = "https://web.umons.ac.be/en/training-offer/"

# ------------------------------------------------------------------

crawl-ucl:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/ucl_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/ucl_${YEAR}.json; fi
	scrapy runspider ${CRAWLER_FOLDER}/ucl.py

crawl-ulb:
	if [ -f data/ulb_${YEAR}.json ]; then rm data/ulb_${YEAR}.json; fi
	scrapy runspider ${CRAWLER_FOLDER}/ulb.py

crawl-uantwerp:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/uantwerp_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/uantwerp_${YEAR}.json; fi
	scrapy runspider ${CRAWLER_FOLDER}/ucl.py

crawl-ugent:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/ugent_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/ugent_${YEAR}.json; fi
	scrapy runspider ${CRAWLER_FOLDER}/ugent_webdriver.py

crawl-kuleuven:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}/kuleuven_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/kuleuven_${YEAR}.json; fi
	scrapy runspider ${CRAWLER_FOLDER}/kuleuven.py

crawl-umons:
	if [ -f ${CRAWLING_OUTPUT_FOLDER}//umons_${YEAR}.json ]; then rm ${CRAWLING_OUTPUT_FOLDER}/umons_${YEAR}.json; fi
	scrapy runspider ${CRAWLER_FOLDER}/umons.py 

#--------------------------------------------------------------------

score-ucl:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/ucl_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/ucl_scoring_${YEAR}.csv
	python ${SCORING_FOLDER}/prepare_to_web.py --school "ucl" --year ${YEAR}

score-ulb:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/ulb_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/ulb_scoring_${YEAR}.csv
	python ${SCORING_FOLDER}/prepare_to_web.py --school "ulb" --year ${YEAR}

score-uantwerp:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/uantwerp_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/uantwerp_scoring_${YEAR}.csv
	python ${SCORING_FOLDER}/prepare_to_web.py --school "uantwerp" --year ${YEAR}

score-ugent:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/ugent_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/ugent_scoring_${YEAR}.csv
	python ${SCORING_FOLDER}/prepare_to_web.py --school "ugent" --year ${YEAR}

score-kuleuven:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/kuleuven_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/kuleuven_scoring_${YEAR}.csv
	python ${SCORING_FOLDER}/prepare_to_web.py --school "kuleuven" --year ${YEAR}

score-unamur:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/unamur_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/unamur_scoring_${YEAR}.csv --field "content"
	python ${SCORING_FOLDER}/prepare_to_web.py --school "unamur" --year ${YEAR}

score-uliege:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/uliege_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/uliege_scoring_${YEAR}.csv --field "content"
	python ${SCORING_FOLDER}/prepare_to_web.py --school "uliege" --year ${YEAR}

score-umons:
	python ${SCORING_FOLDER}/score_script.py --input ${CRAWLING_OUTPUT_FOLDER}/umons_courses_${YEAR}.json --output ${SCORING_OUTPUT_FOLDER}/umons_scoring_${YEAR}.csv
	python ${SCORING_FOLDER}/prepare_to_web.py --school "umons" --year ${YEAR}

# -----------------------------

virtual-env:
	if [ -f venv ]; then source venv/bin/activate; fi
