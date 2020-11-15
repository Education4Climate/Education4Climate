import PyPDF2
from w3lib.html import remove_tags

def is_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False

def read_pdf():
    pdfFileObj = open('/home/noel/Téléchargements/A000186.pdf', 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    page_content = ''
    for page_nb in range(pdfReader.numPages):
        page_content += pdfReader.getPage(page_nb).extractText()

    pdfFileObj.close()
    with open("/home/noel/Téléchargements/A000186.txt", "w") as text_file:
        text_file.write(page_content)
    return page_content

    def cleanup(data):
        if data is None:
            return ""
        elif isinstance(data, list):
            result = list()
            for e in data:
                result.append(cleanup(e))
            return result
        else:
            return remove_tags(data).strip()