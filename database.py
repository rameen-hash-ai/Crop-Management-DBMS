#sqlalchemy is ORM(object relational mapper) this allows to work with database tables as python classes instead of writing sql queries
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#This file to connect to the database and create a session for database operations and tells pytho how to talk to postgresql database
DATABASE_URL="postgresql://postgres:080305@localhost:5432/crop_management_db"
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
base=declarative_base()