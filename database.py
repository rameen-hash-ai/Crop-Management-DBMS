#sqlalchemy is ORM(object relational mapper) this allows to work with database tables as python classes instead of writing sql queries
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger=logging.getLogger(__name__)


#This file to connect to the database and create a session for database operations and tells pytho how to talk to postgresql database
DATABASE_URL=os.getenv("DATABASE_URL","postgresql://postgres:080305@localhost:5432/crop_db")
engine=create_engine(DATABASE_URL,poolclass=QueuePool, pool_size=20, max_overflow=40,pool_pre_ping=True,echo=False)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
base=declarative_base()

def TestConnection():
    try:
        conn=psycopg2.connect(host="localhost",database="crop_db",user="postgres",password="080305")
        print("Database connection successful")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models import User,Field,region,Satellite,CropCycle,Weather,Alert
    base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

if __name__=="__main__":
    if TestConnection():
        init_db()