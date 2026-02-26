import os
import pandas as pd
from database import SessionLocal,engine
import models
#importing the database session and engine from database.py and models from models.py to create tables and seed data into the database

models.base.metadata.create_all(bind=engine)#create tables in postges
db=SessionLocal()
df_users=pd.read_csv("User_Punjab_Pakistan.csv")

for _,row in df_users.iterrows():
    user=models.User(name=row["name"],role=row["role"],email=row["email"])
    db.add(user)


db.commit() 
db.close()



