### Note d'Aric: Pourquoi et comment ne pas utiliser un launcher 'artisanal'

#### Pourquoi?
On n'utilise alors pas le paramétrage du scraper.

#### Comment?
Pour lancer un crawler et le debugger sous Pycharm :
- Run / Edit configurations
- Choisir la configuration à modifier
- Switcher "Script path" par "Module name" et écrire : scrapy.cmdline
- Parameters : runspider unicrawl/spiders/{nom du script.py}
- Working directory : {chemin absolu de votre dossier unicrawl}\src\crawl