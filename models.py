import os
import dotenv
dotenv.load_dotenv()
import sqlitecloud
conn_string = os.getenv('connecion-string-sqlite')
def init_db():
    # conn = sqlite3.connect("conversations.db")
    conn = sqlitecloud.connect(f"{conn_string}")
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
def creat_history(messages):
    history = []
    for mess in messages:
     history.append({
        "role": mess[1],
        "parts": [{"text": mess[0]}]
     })
    return history
def get_messages(mess):
    conn = sqlitecloud.connect(f"{conn_string}")
    c = conn.cursor()
    c.execute("select content, sender from message where conv_id = ? order by id;",(mess,))
    messages = c.fetchall()
    return messages
def save_messsage(content,sender,conv_id):
     try:
        # conn = sqlite3.connect("conversations.db")
        conn = sqlitecloud.connect(f"{conn_string}")
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
def save_conversation(new_conv) :
    conn = sqlitecloud.connect(f"{conn_string}")
    c = conn.cursor()
    c.execute("""
        INSERT INTO conversations (adress_ip, start_date, browser_string)
        VALUES (?, ?, ?)
        """, (new_conv["adress_ip"], new_conv["start_date"], new_conv["browser_string"]))
    conn.commit()
    return c.lastrowid