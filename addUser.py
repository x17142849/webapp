import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from sqlalchemy import Date 
from tabledef import engine
import os

 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 

user = User("student",(hashlib.sha512((str('password1')).encode('utf-8'))).hexdigest(),"x17142849@student.ncirl.ie")
session.add(user)
 
session.commit()
