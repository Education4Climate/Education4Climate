# Macros

ULB_URL="https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes"
UCL_URL="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-2019.html"

# ------------------------------------------------------------------



# ------------------------------------------------------------------

test-ulb:
	scrapy shell ${ULB_URL}

test-ucl:
	scrapy shell ${UCL_URL}

# ------------------------------------------------------------------
generate-ucl:
	if [ -f data/ucl_test.json ]; then rm data/ucl_test.json; fi
	python3 crawl/ucl.py --output data/ucl_test.json

generate-ulb:
	if [ -f data/ulb_test.json ]; then rm data/ulb_test.json; fi
	python3 crawl/ulb.py --output data/ulb_test.json

