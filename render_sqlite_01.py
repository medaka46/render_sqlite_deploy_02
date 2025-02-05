import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

app = FastAPI()

db_path = 'example.db'

# Create the database engine
engine = create_engine(f'sqlite:///{db_path}')
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

# Create tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to the User Management API"}

@app.post("/add-user/")
def add_user(name: str, age: int):
    session = Session()
    new_user = User(name=name, age=age)
    session.add(new_user)
    session.commit()
    session.close()
    return {"message": f"Added new user: {name}"}

@app.get("/users/")
def get_users():
    session = Session()
    users = session.query(User).all()
    session.close()
    return [{"id": user.id, "name": user.name, "age": user.age} for user in users]

@app.get("/download/database/")
def download_database():
    if os.path.exists(db_path):
        return FileResponse(db_path, media_type='application/octet-stream', filename=os.path.basename(db_path))
    else:
        raise HTTPException(status_code=404, detail="Database file not found")

@app.get("/download/csv/")
def download_csv():
    session = Session()
    query = "SELECT * FROM users"
    df = pd.read_sql(query, engine)
    session.close()
    
    csv_file_path = "data.csv"
    df.to_csv(csv_file_path, index=False)
    
    return FileResponse(csv_file_path, media_type='text/csv', filename='data.csv')

# To run the FastAPI app, use the command:
# uvicorn hohetto_st_sqlite_deploy_01.hoheto_st_sqlite_01:app --reload