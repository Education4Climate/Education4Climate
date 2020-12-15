from w3lib.html import remove_tags


# TODO: elle sert à quoi cette fonction?
def is_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def read_pdf():

    import PyPDF2

    pdf_file_obj = open('/home/noel/Téléchargements/A000186.pdf', 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)

    page_content = ''
    for page_nb in range(pdf_reader.numPages):
        page_content += pdf_reader.getPage(page_nb).extractText()

    pdf_file_obj.close()
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
