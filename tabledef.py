from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date,DateTime,func, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
#from database import Base
 
engine = create_engine('sqlite:///app.db', echo=True)
Base = declarative_base()
 
########################################################################
class User(Base):
    """"""
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    email    = Column(String, unique=True)
    registered_on = Column(DateTime, default=func.now())     
    door_operated = Column(DateTime, ForeignKey('door_controll.date'))
    #----------------------------------------------------------------------
    def __init__(self, username, password,email):
        """"""
        self.username = username
        self.password = password  
        self.email    = email


class Door_control(Base):
    __tablename__ = "door_control"
    contid =  Column(Integer, primary_key=True)
    cdate = Column(String)
    ctime = Column(String)
#    userid = Column(Integer,ForeignKey('users.id'))
    operated_by = Column(String)#relationship("User",uselist=False,backref="door_controll")
    operation = Column(String)
    method = Column(String)

    def __init__(self,cdate,ctime,operated_by,operation,method):
        self.cdate = cdate
        self.ctime = ctime
        self.operated_by = operated_by
        self.operation = operation
        self.method = method


class Bell_ring(Base):
    __tablename__ = "bell_ring"
    rind_id =  Column(Integer, primary_key=True)
    cdate = Column(String)
    ctime = Column(String)
    mail_sent = Column(String)
    sms_sent  = Column(String)

    def __init__(self,cdate,ctime, mail_sent,sms_sent):
        self.cdate = cdate
        self.ctime = ctime
        self.mail_sent = mail_sent
        self.sms_sent = sms_sent
    	
# create tables
Base.metadata.create_all(engine)
