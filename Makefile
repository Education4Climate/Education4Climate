# Macros

ULB_URL="https://www.ulb.be/fr/programme/lien-vers-catalogue-des-programmes"
UCL_URL="https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-2019.html"

# ------------------------------------------------------------------

test-ulb:
	scrapy shell ${ULB_URL}

test-ucl:
	scrapy shell ${UCL_URL}

# ------------------------------------------------------------------

generate-ulb:
	[ -f data/ulb_test.json ] && rm data/ulb_test.json #Delete the file if already exists
	python3 crawl/ulb.py --output data/ulb_test.json

generate-ucl:
	#[ -f data/ucl_test.json ] && rm data/ucl_test.json || echo "New file will be created"
	python3 crawl/ucl.py --output data/ucl_test.json

