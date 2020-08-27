import sys
from datetime import datetime
import mysql.connector
from gtts import gTTS
import os
import speech_recognition as sr
# obtain audio from the microphone
r = sr.Recognizer()
import requests
import json



db_bot = mysql.connector.connect(
  host      =   "<host mysql>",
  user      =   "<user mysql>",
  passwd    =   "<password mysql>",
  database  =   "<db name>"
)

db_bot_cursor   = db_bot.cursor(buffered=True)

def search_data(cursor,tabel,data):
    sql_search = "SELECT answer FROM "+tabel+" WHERE question LIKE '%"+data+"%' order by rand()"
    cursor.execute(sql_search)
    data_response_search = cursor.fetchone()
    if data_response_search == None :
        return search_simsimi(data)
    else:
        return data_response_search

def search_simsimi(data_tanya):
    url_simsimi = 'https://wsapi.simsimi.com/190410/talk'
    headers = {'Content-Type': 'application/json','x-api-key': '<your api key>'}
    data = '{"utext":"'+data_tanya+'","lang": "id"}'
    response = requests.post(url_simsimi, headers=headers, data=data)
    response_json = response.json()
    # if response_json['message'] == "Limit Exceeded Exception":
    #     return None
    # else:
    jawaban_simsimi = response_json['atext']
    if jawaban_simsimi == '' :
        return None
    else:
        insert_data(db_bot,db_bot_cursor,'tabel_ilmu',data_tanya,jawaban_simsimi)
        jawaban_baru = search_data(db_bot_cursor,'tabel_ilmu',data_tanya)
        return jawaban_baru

def insert_data(db_bot,cursor,tabel,data_question,data_answer):
    sql_insert = "INSERT INTO "+tabel+" (question,answer) VALUES (%s, %s)"
    val_insert = (data_question, data_answer)
    cursor.execute(sql_insert, val_insert)
    db_bot.commit()
    response_data = cursor.rowcount
    return response_data

def menjawab(text_voice):
    #myobj = gTTS(text=text_voice, lang='id', slow=False)
    #myobj.save("say.mp3")
    #os.system("mpg321 say.mp3")
    os.system("espeak -v mb-id1 -k5 -s150 '"+text_voice+"'")

def mendengar():
    with sr.Microphone() as source:
        audio = r.listen(source,timeout=1,phrase_time_limit=10)
        try:
            data = r.recognize_google(audio, language = 'id-ID')
        except sr.UnknownValueError:
            data = "error"
        except sr.RequestError as e:
            data = "error"
    return data

def mencari(pertanyaan):
    data_ilmu = search_data(db_bot_cursor,'tabel_ilmu',pertanyaan)
    if data_ilmu != None :
        #ketemu
        print("yazabot: "+data_ilmu[0]+"")
        menjawab(data_ilmu[0]+"")
        # menjawab("Ada lagi yang mau ditanyakan ?")
        pernyataan = mendengar()
        mencari(pernyataan)
    else:
        print("yazabot: Bantu aku dong, Apa jawaban dari pertanyaan "+pertanyaan+" ?")
        menjawab("Bantu aku dong, Apa jawaban dari pertanyaan "+pertanyaan+" ?")
        jawaban = mendengar()
        belajar(pertanyaan,jawaban)

def belajar(pertanyaan_belajar,jawaban_belajar):
    set_otak        = insert_data(db_bot,db_bot_cursor,'tabel_ilmu',pertanyaan_belajar,jawaban_belajar)
    if set_otak == 1 :
        print("yazabot: Terima Kasih Sudah Mengajari Aku")
        menjawab("Terima Kasih Sudah Mengajari Aku")
        print("yazabot: Ada lagi yang bisa aku bantu ?")
        menjawab("Ada lagi yang bisa aku bantu ?")
        pertanyaan = mendengar()
        mencari(pertanyaan)
    else:
        print("yazabot: Aku Masih Belum Mengerti")
        menjawab("Aku Masih Belum Mengerti")


print("yazabot: Yazabot disini , ada yang bisa aku bantu?")
menjawab("Yazabot disini , ada yang bisa aku bantu?")
pertanyaan = mendengar()
mencari(pertanyaan)
