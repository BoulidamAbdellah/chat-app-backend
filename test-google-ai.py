import  google.generativeai as genai
from pypdf import PdfReader
import json
from flask_cors import CORS
import filelock
import sqlite3
from datetime import datetime 
import sqlitecloud
# creating a pdf reader object
reader = PdfReader('C:/Users/dell/Downloads/CV_Abdellah_Boulidam_Data_Engineer.pdf')
def init_db():
    # conn = sqlite3.connect("conversations.db")
    conn = sqlitecloud.connect("sqlitecloud://cb1l46cynz.g5.sqlite.cloud:8860/conversations.db?apikey=JZgfJLtmQvtTyBCBR39gAo5zC90TOjHDKR7KD5TCOoo")
    c = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON")
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            start_date TEXT ,
            browser_string TEXT ,
            adress_ip TEXT
        )
    """)
    conn.commit()
    c.execute("""CREATE TABLE IF NOT EXISTS message (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 content TEXT ,
                 conv_id INTEGER,
                sender TEXT CHECK(sender IN ('model', 'user')),
                FOREIGN KEY (conv_id) REFERENCES conversations(id) ON DELETE CASCADE
              )""")
    conn.close()

# Appeler cette fonction une fois au démarrage
init_db()
# printing number of pages in pdf file
print(len(reader.pages[0].extract_text()))

def creat_history(messages):
    history = []
    for mess in messages:
     history.append({
        "role": mess[1],
        "parts": [{"text": mess[0]}]
     })
    return history 
def save_messsage(content,sender,conv_id):
     try:
        # conn = sqlite3.connect("conversations.db")
        conn = sqlitecloud.connect("sqlitecloud://cb1l46cynz.g5.sqlite.cloud:8860/conversations.db?apikey=JZgfJLtmQvtTyBCBR39gAo5zC90TOjHDKR7KD5TCOoo")
        c = conn.cursor()
        c.execute("""
            INSERT INTO message (content, sender, conv_id)
            VALUES (?, ?, ?)
        """, (content, sender, conv_id))
        conn.commit()
        conn.close()
        print("Message enregistré avec succès.")
     except Exception as e:
        print("Erreur lors de l'enregistrement du message :", e)
# getting a specific page from the pdf file
page = reader.pages[0]

# extracting text from page
cv_data = page.extract_text()
genai.configure(api_key="AIzaSyBH_NLH_puGbtK6FNaED6SSCik7yHUt_Ss")
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
chat = model.start_chat(history=[])
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
 conn = sqlitecloud.connect("sqlitecloud://cb1l46cynz.g5.sqlite.cloud:8860/conversations.db?apikey=JZgfJLtmQvtTyBCBR39gAo5zC90TOjHDKR7KD5TCOoo")

 c = conn.cursor()
 if mess == "false" :
     print(request.remote_addr)
     new_conv = {"adress_ip" :request.remote_addr,"start_date":datetime.now(),"browser_string":data["browser_string"]}
     c.execute("""
        INSERT INTO conversations (adress_ip, start_date, browser_string)
        VALUES (?, ?, ?)
        """, (new_conv["adress_ip"], new_conv["start_date"], new_conv["browser_string"]))
     conn.commit()
     convnumber = c.lastrowid
     print(convnumber)
     chat = model.start_chat(history=[])
     conversation_chat[str(convnumber)] = chat
     return jsonify({"convnumber": convnumber })
 else :
  c.execute("select content, sender from message where conv_id = ? order by id;",(mess,))
  messages = c.fetchall()
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