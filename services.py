from pypdf import PdfReader
import dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
def get_pdf_extracted():
    dotenv.load_dotenv()
    reader = PdfReader(f"{os.getenv('pdf_cv_path')}")
    page = reader.pages[0]
    cv_data = page.extract_text()
    return cv_data
def get_pdf_extracted1():
    creds = service_account.Credentials.from_service_account_file(
        'google-drive-service-key.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    file_id = os.getenv('pdf_id')  # ou tu peux mettre directement ton ID

    # Télécharger le fichier PDF en mémoire
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Téléchargement en mémoire : {status.progress() * 100:.2f}%")

    fh.seek(0)  # Important : remettre le curseur au début du buffer

    # Maintenant lire le PDF directement depuis le BytesIO avec PyPDF2
    reader = PdfReader(fh)
    page = reader.pages[0]
    cv_data = page.extract_text()
    return cv_data
def get_sys_instruction():
    f = open('system_instruction.txt','r')
    sys_instr = f.read()
    pdf_data = get_pdf_extracted1()
    return  sys_instr.replace("{{cv-data}}",pdf_data)
