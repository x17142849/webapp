#!/usr/bin/env python
import re
from importlib import import_module
from flask import Flask,session,g,abort, render_template, Response, request, jsonify, url_for,redirect, abort,flash
import sys
import os
import time
import datetime
from datetime import datetime
import thread
from grovepi import *
import math
import threading
import picamera
import cv2
import socket
import io
import sqlite3
#import send_nexmo_sms as sms
import nexmo
from camera_pi import Camera
from multiprocessing import Value
import requests
from flask_mail import Mail, Message

#receive mail

from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import re
import dateutil.parser as parser

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists, func
from sqlalchemy.orm import sessionmaker
from tabledef import *
import hashlib
from os.path import join, dirname
from dotenv import load_dotenv
#sms

#import door_alarm as alarm

#alarm

buzzer_pin = 2 #Port for the buzzer
button = 4 #port for the button
LED = 3
relay_pin = 7
ultrasonic_range = 8


pinMode(buzzer_pin,"OUTPUT")
pinMode(button,"INPUT")
pinMode(LED,"OUTPUT")
button_status = 0
button_state = 0

pinMode(ultrasonic_range,"INPUT")
 

app = Flask(__name__)



#send email
#app.config['MAIL_SERVER']='smtp.gmail.com'
#app.config['MAIL_PORT'] = 465
#app.config['MAIL_USERNAME'] = 'mysmartdoorbell@gmail.com'
#app.config['MAIL_PASSWORD'] = 'Perf.H0t'
#app.config['MAIL_USE_TLS'] = False
#app.config['MAIL_USE_SSL'] = True
#mail = Mail(app)

engine = create_engine('sqlite:///app.db', echo=True) 


#receive mail



@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(request.args.get('next') or url_for('index'))



#sms
app.config.from_pyfile('.env')
import sms
import voice

mail = Mail(app)



@app.route('/login', methods=['POST'])
def login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = (hashlib.sha512((str(request.form['password'])).encode('utf-8'))).hexdigest()
 
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        session['logged_in'] = True
        session['username'] = POST_USERNAME
    else:
        flash('wrong password!')
    return redirect(request.args.get('next') or url_for('index'))



@app.route('/')
#@login_required
def index():    
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html', uptime=GetUptime())

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    videoState = request.args.get('videoState')
    return Response(gen(Camera()),mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route("/led")
def led():
    state = request.args.get('state')
    if state=="on":
        digitalWrite(LED,1)
    else:
        digitalWrite(LED,0)
    return ""


@app.route("/door")
def door():
    op = ""
    doorState = request.args.get('doorState')
    if doorState=="open":
        digitalWrite(relay_pin,0)
        op = "unlock"
    else:
        digitalWrite(relay_pin,1)
        op = "lock"
    if 'username' in session:
        username = session['username']
        doorState = doorState+" "+insert_dbd(username,op)        
    return doorState

def insert_dbd(username ,op):
    ctime = str(time.strftime("%X"))
    cdate = str(time.strftime("%x"))

    msg = ""
    import sqlite3 as sql
    try:
        with sql.connect("app.db") as con:

            cur = con.cursor()
            cur.execute("insert into door_control (cdate,ctime,operated_by,operation,method) values (?,?,?,?,?)",(cdate,ctime,username,op,"web"))
            con.commit()
            msg = "Successfully inserted"
    except sql.Error as e:
        msg = "Database error: "+ str(e)
        print("Error in insert operation")
        con.rollback()
    except Exception as e:
        msg = "Exception in _query: "+ str(e)

    finally:
        if con:
            con.close()
        return msg




@app.route("/send_mail")
def send_mail():
    dotenv_path = join(dirname(__file__), './.env')
    load_dotenv(dotenv_path)
#    msg = Message('Smart doorbell notification',sender='mysmartdoorbell@gmail.com',recipients=['x17142849@student.ncirl.ie'])
    msg = Message('Smart doorbell notification',sender=os.getenv('MAIL_USERNAME'),recipients=[os.getenv('MAIL_RECIPIENT')])
    msg.body = 'Hello, a new doorbell at '+str(time.strftime("%X"))
    mail.send(msg)
    return 'Mail notification sent!'


@app.route("/sms/send")
def send_sms():
    return jsonify(sms.send(app.config))


@app.route("/readmail")
def readmail():
    # Creating a storage.JSON file with authentication details
    SCOPES = 'https://www.googleapis.com/auth/gmail.modify' # we are using modify and not readonly, as we will be marking the messages Read
    store = file.Storage('storage.json') 
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))

    user_id =  'me'
    label_id_one = 'INBOX'
    label_id_two = 'UNREAD'

    # Getting all the unread messages from Inbox
    # labelIds can be changed accordingly
    unread_msgs = GMAIL.users().messages().list(userId='me',labelIds=[label_id_one, label_id_two]).execute()

    # We get a dictonary. Now reading values for the key 'messages'
    mssg_list = []

    try:
        mssg_list = unread_msgs['messages']
    except Exception as e:
        pass

#    print ("Total unread messages in inbox: ", str(len(mssg_list)))

    final_list = [ ]

    for mssg in mssg_list:
        temp_dict = { }
        m_id = mssg['id'] # get id of individual message
        message = GMAIL.users().messages().get(userId=user_id, id=m_id).execute() # fetch the message using API
        payld = message['payload'] # get payload of the message 
        headr = payld['headers'] # get header of the payload

        for one in headr: # getting the Subject
            if one['name'] == 'Subject':
                msg_subject = one['value']
                temp_dict['Subject'] = msg_subject
            else:
                pass

        for two in headr: # getting the date
            if two['name'] == 'Date':
                msg_date = two['value']
                date_parse = (parser.parse(msg_date))
                m_date = (date_parse.date())
                temp_dict['Date'] = str(m_date)
            else:
                pass

        for three in headr: # getting the Sender
            if three['name'] == 'From':
                msg_from = three['value']
                temp_dict['Sender'] = msg_from
            else:
                pass
        
        temp_dict['Snippet'] = message['snippet'] # fetching message snippet


        try:
		
            # Fetching message body
            mssg_parts = payld['parts'] 
            part_one  = mssg_parts[0]  
            part_body = part_one['body'] 
            part_data = part_body['data']
            clean_one = part_data.replace("-","+") 
            clean_one = clean_one.replace("_","/") 
            clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) 
            soup = BeautifulSoup(clean_two , "lxml" )
            mssg_body = soup.body()
            temp_dict['Message_body'] = mssg_body

        except :
            pass

        print (temp_dict)
        final_list.append(temp_dict) # Create a dictonary item in the final list
	
    try:
        for mail in final_list:
            if 'Subject' in mail and 'Sender' in mail:
                operation = ""
                
                if mail['Subject'] == 'lockdoor' and process_email(str(mail['Sender'])):
                    requests.get('http://localhost/door?doorState=locked').content
                    GMAIL.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute() 
                    operation = 'lock' + insert_db(str(mail['Sender']),operation)
                elif  mail['Subject'] == 'unlockdoor' and  process_email(str(mail['Sender'])):
                    requests.get('http://localhost/door?doorState=open').content
                    GMAIL.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute() 
                    operation = "unlock " + insert_db(str(mail['Sender']),operation)
                else:
                    operation = 'forbiden'
                    return "forbiden"

                #Mark the messagea as read
                return operation
        
    except Exception as e:
        pass
    finally:
        return str(final_list)


def process_email(sender):
    email = sender[sender.find("<")+1:sender.find(">")]
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(exists().where(User.email==email))
    result = query.scalar()
    s.close()
    return result

def insert_db(sender ,op):
    _email = sender[sender.find("<")+1:sender.find(">")]
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.email==str(_email))
    _row = query.first()
    username = _row.username
    id = _row.id
    ctime = str(time.strftime("%X"))
    cdate = str(time.strftime("%x"))
    

    msg = ""
    import sqlite3 as sql
    try:
        with sql.connect("app.db") as con:

            cur = con.cursor()
            cur.execute("insert into door_control (cdate,ctime,operated_by,operation,method) values (?,?,?,?,?)",(cdate,ctime,username,op,_email))
            con.commit()
            msg = "Successfully inserted"
    except sql.Error as e:
        msg = "Database error: "+ str(e)
        print("Error in insert operation")
        con.rollback()
    except Exception as e:
        msg = "Exception in _query: "+ str(e)

    finally:
        if con:
            con.close()
        s.close()
        return msg

        



@app.route("/_button")
def _button():

    button_status = digitalRead(button)    
    if button_status:
        emailState = request.args.get('emailState')
        smsState = request.args.get('smsState')
        state = "pressed"
        digitalWrite(buzzer_pin,1)
        #time.sleep(2)
        if emailState == "email-on":
            state = requests.get('http://localhost/send_mail').content
        if smsState == "sms-on":
            state = state + " "+ requests.get('http://localhost/sms/send').content
        insert_dbb(emailState,smsState)        
    else:
        state = ""
        digitalWrite(buzzer_pin,0)
    requests.get('http://localhost/readmail').content
    return jsonify(buttonState=state)


def insert_dbb(emailState ,smsState):
    ctime = str(time.strftime("%X"))
    cdate = str(time.strftime("%x"))

    msg = ""
    import sqlite3 as sql
    try:
        with sql.connect("app.db") as con:

            cur = con.cursor()
            cur.execute("insert into bell_ring (cdate,ctime,mail_sent,sms_sent) values (?,?,?,?)",(cdate,ctime,emailState,smsState))
            con.commit()
            msg = "Successfully inserted"
    except sql.Error as e:
        msg = "Database error: "+ str(e)
        print("Error in insert operation")
        con.rollback()
    except Exception as e:
        msg = "Exception in _query: "+ str(e)

    finally:
        if con:
            con.close()
        return msg

    

def GetUptime():
    from subprocess import check_output
    output = check_output(["uptime"])
    uptime = output[output.find("up"):output.find("user")-5]
    return uptime



if __name__ == '__main__':

    app.secret_key = os.urandom(12)	
    try:
        app.run(debug=True, host='0.0.0.0',port=80, threaded=True)
    except KeyboardInterrupt:
        os.system("kill -9 $(ps aux | grep app.py | awk '{print $2}'")

    
