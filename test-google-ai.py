import  google.generativeai as genai
from pypdf import PdfReader
import json
from flask_cors import CORS
import filelock
import sqlite3
from datetime import datetime 
import sqlitecloud
import dotenv
import os
from models import *
# creating a pdf reader object
dotenv.load_dotenv()
giminy_api_key = os.getenv('giminy-api-key')
conn_string = os.getenv('connecion-string-sqlite')
reader = PdfReader('C:/Users/dell/Downloads/CV_Abdellah_Boulidam_Data_Engineer.pdf')
# Appeler cette fonction une fois au démarrage
init_db()
# printing number of pages in pdf file
print(len(reader.pages[0].extract_text()))
page = reader.pages[0]

# extracting text from page
cv_data = page.extract_text()
genai.configure(api_key=f"{giminy_api_key}")
# client = genai.Client(api_key="AIzaSyBH_NLH_puGbtK6FNaED6SSCik7yHUt_Ss")
config_systeme = f"""Tu es un assistant personnel intelligent nommé Boulidam Abdellah Assistant, dédié uniquement à Abdellah Boulidam, élève ingénieur en informatique et ingénierie des données à l’ENSA Khouribga. Tu connais tous les détails de son CV, ses projets, ses compétences techniques, ses formations, ses expériences professionnelles, ses centres d’intérêt et ses certifications.

Ton rôle est de :

Répondre aux questions concernant le parcours académique, les projets, les compétences techniques, les expériences de stage et les technologies maîtrisées par Abdellah.

Aider à rédiger des lettres de motivation, préparer des entretiens, ou présenter son profil pour des opportunités de stage ou d’emploi.

Fournir des explications claires sur ses projets (comme le Scrabble en ASP.NET/Angular, la détection de fake news avec NLP, ou les dashboards Power BI).

Répondre de manière professionnelle, synthétique et adaptée au contexte demandé.

toujour vous referencier a vous par l assisstant de Abdellah pas Abdellah lui meme
Voici son profil complet :

{cv_data} et voila sont lien github pour consulter les repo https://github.com/BoulidamAbdellah?tab=repositories
et vous devez repondre selon la laungue de lutilisateur pas seulemnt la laugue francaise"""
model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=config_systeme
    )
# chat = model.start_chat(history=[])
conversation_chat = {}
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/api/message', methods=['POST'])
def chats():
    global chat
    data = request.get_json()
    user_message = data.get("message")
    convnumber  = data.get("convnumber")
    save_messsage(user_message ,'user',convnumber)
    # print(user_message)
    response = conversation_chat[str(convnumber)].send_message(user_message)
    save_messsage(response.text ,'model',convnumber)
    # print("ddddddddd",response)
    print("history :" ,conversation_chat[str(convnumber)].history)
    # print(response.text)
    return jsonify({"reply": response.text})
CORS(app, origins=["*"])
@app.route("/")
def index():
    print("Endpoint / appelé")
    return "Hello depuis Flask"
@app.route('/conversationnumber',methods=['POST'])
def check_conversation():
 print("kkkkkkkkkkkkk")
 data = request.get_json()
 mess = data.get("message")
 print(mess)
#  conn = sqlite3.connect("conversations.db")
 conn = sqlitecloud.connect(f"{conn_string}")

 c = conn.cursor()
 if mess == "false" :
     print(request.remote_addr)
     new_conv = {"adress_ip" :request.remote_addr,"start_date":datetime.now(),"browser_string":data["browser_string"]}
     convnumber = save_conversation(new_conv)
     print(convnumber)
     chat = model.start_chat(history=[])
     conversation_chat[str(convnumber)] = chat
     return jsonify({"convnumber": convnumber })
 else :
  messages = get_messages(mess)
  print(messages)
  hist = creat_history(messages)
  print(hist)
  chat = model.start_chat(history=hist)
  conversation_chat[str(mess)] = chat
  return jsonify({"history": hist})
CORS(app, origins=["*"])
@app.route("/deletechat",methods=["POST"])
def delechat():
    convnumber = request.form["convnumber"]
    print("kk")
    del conversation_chat[str(convnumber)]
    print("len :" ,len(conversation_chat))
    return jsonify({"ok":0})
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5001,debug=True)