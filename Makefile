# Macros

export YEAR ?= 2023

CRAWLER_FOLDER = src/crawl/unicrawl/spiders
SCORING_FOLDER = src/score

CRAWLING_OUTPUT_FOLDER = data/crawling-output
SCORING_OUTPUT_FOLDER = data/scoring-output

# ------------------------------------------------------------------

SCHOOLS := $(subst _programs,,$(notdir $(basename $(wildcard $(CRAWLER_FOLDER)/*_programs.py))))

crawl:
	@$(MAKE) $(addprefix crawl-,$(SCHOOLS))

$(CRAWLING_OUTPUT_FOLDER)/%_$(YEAR).json: LOG_FILE = ../$(basename $@).log

# output file is sorted by id so that we can make year-over-year comparisons more easily
$(CRAWLING_OUTPUT_FOLDER)/%_$(YEAR).json:
	@cd src && \
		if scrapy runspider crawl/unicrawl/spiders/$*.py > $(LOG_FILE) 2>&1; then \
		  	(echo "["; jq -r --compact-output '. | sort_by(.id) | .[]' ../$@ | sed '$$!s/$$/,/'; echo "]") > ../$@.tmp; \
		  	mv ../$@.tmp ../$@; \
			rm -f $(LOG_FILE); \
		fi

clean-crawl:
	@rm -f $(CRAWLING_OUTPUT_FOLDER)/*_$(YEAR)*.json*
	@rm -f $(CRAWLING_OUTPUT_FOLDER)/*.log

clean-crawl-%:
	@rm -f $(CRAWLING_OUTPUT_FOLDER)/$**_$(YEAR)*.json*
	@rm -f $(CRAWLING_OUTPUT_FOLDER)/$**.log

crawl-%:
	@$(MAKE) $(CRAWLING_OUTPUT_FOLDER)/$*_programs_$(YEAR).json
	@$(MAKE) $(CRAWLING_OUTPUT_FOLDER)/$*_courses_$(YEAR).json

format-crawling-output: $(CRAWLING_OUTPUT_FOLDER)/*.json
	for file in $^; do \
  		(echo "["; jq -r --compact-output '. | sort_by(.id) | .[]' $${file} | sed '$$!s/$$/,/'; echo "]") > $${file}.tmp; \
		mv $${file}.tmp $${file}; \
  	done

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
