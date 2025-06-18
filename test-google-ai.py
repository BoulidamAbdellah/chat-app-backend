import  google.generativeai as genai
from datetime import datetime 
import dotenv
import os
from models import *
from services import *
from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
# creating a pdf reader object
dotenv.load_dotenv()
giminy_api_key = os.getenv('giminy-api-key')
# Appeler cette fonction une fois au démarrage
init_db()
genai.configure(api_key=f"{giminy_api_key}")
config_systeme = get_sys_instruction()
model = genai.GenerativeModel(model_name='gemini-2.0-flash',  system_instruction=config_systeme)
# chat = model.start_chat(history=[])
conversation_chat = {}
# scheduler = BackgroundScheduler()
# def modifie_sys_instruction():
#     global model
#     model =  genai.GenerativeModel(model_name='gemini-2.0-flash',  system_instruction=get_sys_instruction())
# # 2. Ajouter la tâche avec un déclencheur `interval`
# scheduler.add_job(modifie_sys_instruction, 'interval', seconds=40)

# # 3. Démarrer le scheduler
# scheduler.start()
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
@app.route('/conversationnumber',methods=['POST'])
def check_conversation():
 data = request.get_json()
 mess = data.get("message")
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
  hist = creat_history(messages)
  chat = model.start_chat(history=hist)
  conversation_chat[str(mess)] = chat
  print(len(conversation_chat))
  return jsonify({"history": hist})

@app.route("/deletechat",methods=["POST"])
def delechat():
    convnumber = request.form["convnumber"]
    print("kk")
    del conversation_chat[str(convnumber)]
    print("len :" ,len(conversation_chat))
    return jsonify({"ok":0})
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5001,debug=True,use_reloader=False)