import PyPDF2

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
    return page_content