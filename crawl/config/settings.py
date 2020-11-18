YEAR = "2020"
ULB_URL = "https://www.ulb.be/servlet/search?l=0&beanKey=beanKeyRechercheFormation&&types=formation&typeFo=BA&s=FACULTE_ASC&limit=300&page=1"
UCL_URL = "https://uclouvain.be/fr/catalogue-formations/formations-par-faculte-" + YEAR + ".html"
UANTWERP_URL = "https://www.uantwerpen.be/en/study/education-and-training/"
UGENT_URL = "https://studiegids.ugent.be/" + YEAR + "/EN/FACULTY/faculteiten.html"
KULEUVEN_URL = "https://onderwijsaanbod.kuleuven.be/opleidingen/e/index.htm"
VUB_URL = 'https://www.vub.be/en/programmes#'

ABSOLUTE_PATH_DOWNLOAD_FOLDER = '/home/noel/Téléchargements/'

DRIVER_PATH = "/snap/bin/chromium.chromedriver"

# UGENT -------------
SEPARATOR_FIRST_AND_SECOND_PART = 'Offered in the following programmes in  2020-2021crdtsoffering'

LECTURERS_PARAGRAPH_SPLITTER = "Lecturers in academic year " + YEAR + "-" + str(int(YEAR) + 1)
OTHER_CATEGORIES_SEPARATORS = ["Course offerings and teaching methods",
                               "Offered in the following programmes in",
                               "Course size"]
