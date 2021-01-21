### Aric's comment: Why not to use a 'hand-made' launcher and how to do then?

#### Why?
Because if you do, you are not using the parametrization of the scraper.

#### How?
To launch a crawler and the debugger with PyCharm :
- Run / Edit configurations
- Choose the configuration you want to modify
- Switch from "Script path" to "Module name" and write : scrapy.cmdline
- Parameters : runspider unicrawl/spiders/{name of the script.py}
- Working directory : {absolute path to your unicrawl folder}\src\crawl
