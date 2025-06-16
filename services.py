from pypdf import PdfReader
import dotenv
import os
def get_pdf_extracted():
    dotenv.load_dotenv()
    reader = PdfReader(f"{os.getenv('pdf_cv_path')}")
    page = reader.pages[0]
    cv_data = page.extract_text()
    return cv_data
def get_sys_instruction():
    f = open('system_instruction.txt','r')
    sys_instr = f.read()
    pdf_data = get_pdf_extracted()
    return  sys_instr.replace("{{cv-data}}",pdf_data)
    
    
    
    