import os 
import shutil
import PyPDF2


def clean_folder(path):
  if os.path.exists(path):
    shutil.rmtree(path)
  os.makedirs(path)

def read_pdf(path):
  pdf_file_obj = open(path, 'rb')
  pdf_reader=PyPDF2.PdfFileReader(pdf_file_obj)
  page_obj=pdf_reader.getPage(0)
  txt=page_obj.extractText()
  pdf_file_obj.close()

  print(txt)
