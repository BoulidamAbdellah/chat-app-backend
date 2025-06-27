import json
import wave
from pypdf import PdfReader
import pyttsx3
from vosk import Model, KaldiRecognizer,SetLogLevel
import dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pydub import AudioSegment
import io
def get_pdf_extracted1():
    service_key_str = os.environ.get('GOOGLE_SERVICE_KEY')
    service_account_info = json.loads(service_key_str)
    creds = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/drive']
            )
    # creds = service_account.Credentials.from_service_account_file(
    #     'google-drive-service-key.json',
    #     scopes=['https://www.googleapis.com/auth/drive']
    # )
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
    return  sys_instr.replace("{{cv_data}}",pdf_data)


def speech_to_text(file,convnumber):
    # Lire le fichier depuis le blob webm
    os.makedirs("tmp", exist_ok=True)
    file.save(f"tmp/uploaded{convnumber}.webm")  # enregistrer dans un fichier temporaire
    audio = AudioSegment.from_file(f"tmp/uploaded{convnumber}.webm",format="webm")
    # audio = AudioSegment.from_file(file, format="webm")

    # Convertir pour Vosk : mono, 16kHz, 16-bit
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    # Sauvegarde temporaire WAV avec header PCM
    temp_wav = f"tmp/processed{convnumber}.wav"
    audio.export(temp_wav, format="wav")

    # Charger modèle Vosk
    model_path = "vosk-model/vosk-model-small-en-us-0.15"
    SetLogLevel(0)
    model = Model(model_path)

    # Transcrire avec Vosk
    wf = wave.open(temp_wav, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    result_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += res.get("text", "") + " "

    final_res = json.loads(rec.FinalResult())
    result_text += final_res.get("text", "")

    wf.close()
    os.remove(temp_wav)
    os.remove(f"tmp/uploaded{convnumber}.webm") #Nettoyer après traitement

    print("🎙️ Transcription:", result_text.strip())
    return result_text.strip()


# Exemple d'appel
def text_to_speach(convnumber,text):
    filename = f"tmp/output{convnumber}.wav"

    # 1. Générer l'audio
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 180)
    engine.setProperty('volume', 0.9)
    engine.save_to_file(text, filename)
    engine.runAndWait()

    # 2. Lire le fichier en binaire (blob)
    with open(filename, 'rb') as f:
        audio_blob = f.read()

    # 3. Supprimer le fichier temporaire
    os.remove(filename)

    return audio_blob
