from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize FastAPI app
app = FastAPI()

# Database setup
db_path = 'example.db'
engine = create_engine(f'sqlite:///{db_path}')
Base = declarative_base()

# Define the User model for SQLAlchemy
class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

# Create tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Pydantic model for User
class User(BaseModel):
    id: Optional[int] = None
    name: str
    age: int

# Root endpoint
@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <html>
        <head>
            <title>User API</title>
            <style>
                .button {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                }
                .form-container {
                    margin: 20px 0;
                    padding: 20px;
                    border: 1px solid #ddd;
                }
                .input-field {
                    margin: 10px 0;
                    padding: 5px;
                }
                .delete-button {
                    background-color: #f44336;
                }
                .update-button {
                    background-color: #2196F3;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to the User API</h1>
            
            <div class="form-container">
                <h2>Add New User</h2>
                <form id="addUserForm">
                    <input type="text" id="name" placeholder="Name" class="input-field" required><br>
                    <input type="number" id="age" placeholder="Age" class="input-field" required><br>
                    <button type="submit" class="button">Add User</button>
                </form>
            </div>

            <div class="form-container">
                <h2>Update User</h2>
                <form id="updateUserForm">
                    <input type="number" id="updateId" placeholder="User ID" class="input-field" required><br>
                    <input type="text" id="updateName" placeholder="New Name" class="input-field" required><br>
                    <input type="number" id="updateAge" placeholder="New Age" class="input-field" required><br>
                    <button type="submit" class="button update-button">Update User</button>
                </form>
            </div>

            <div class="form-container">
                <h2>Delete User</h2>
                <form id="deleteUserForm">
                    <input type="number" id="deleteId" placeholder="User ID" class="input-field" required><br>
                    <button type="submit" class="button delete-button">Delete User</button>
                </form>
            </div>

            <a href="/users" class="button">View All Users</a>
            <a href="/docs" class="button">API Documentation</a>
            <a href="/download/csv" class="button">Download CSV</a>

            <script>
                document.getElementById('addUserForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const response = await fetch('/users/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: document.getElementById('name').value,
                            age: parseInt(document.getElementById('age').value)
                        }),
                    });
                    if (response.ok) alert('User added successfully!');
                    else alert('Error adding user');
                });

                document.getElementById('updateUserForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const userId = document.getElementById('updateId').value;
                    const response = await fetch(`/users/${userId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: document.getElementById('updateName').value,
                            age: parseInt(document.getElementById('updateAge').value)
                        }),
                    });
                    if (response.ok) alert('User updated successfully!');
                    else alert('Error updating user');
                });

                document.getElementById('deleteUserForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const userId = document.getElementById('deleteId').value;
                    const response = await fetch(`/users/${userId}`, {
                        method: 'DELETE',
                    });
                    if (response.ok) alert('User deleted successfully!');
                    else alert('Error deleting user');
                });
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Create a new user
@app.post("/users/", response_model=User)
def create_user(user: User):
    session = Session()
    db_user = UserDB(name=user.name, age=user.age)
    session.add(db_user)
    session.commit()
    user.id = db_user.id
    session.close()
    
    # Update CSV
    df = pd.read_sql("SELECT * FROM users", engine)
    df.to_csv('users.csv', index=False)
    
    return user

# Get all users
@app.get("/users/", response_class=HTMLResponse)
def get_users():
    session = Session()
    users = session.query(UserDB).all()
    session.close()
    
    html_content = """
    <html>
        <head>
            <title>All Users</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                .user-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                .user-table th, .user-table td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }
                .user-table th {
                    background-color: #4CAF50;
                    color: white;
                }
                .user-table tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                .user-table tr:hover {
                    background-color: #ddd;
                }
                .back-button {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h1>All Users</h1>
            <table class="user-table">
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Age</th>
                </tr>
    """
    
    for user in users:
        html_content += f"""
                <tr>
                    <td>{user.id}</td>
                    <td>{user.name}</td>
                    <td>{user.age}</td>
                </tr>
        """
    
    html_content += """
            </table>
            <br>
            <a href="/" class="back-button">Back to Home</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Get a specific user by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    session = Session()
    user = session.query(UserDB).filter(UserDB.id == user_id).first()
    session.close()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(id=user.id, name=user.name, age=user.age)

# Update a user
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    session = Session()
    user = session.query(UserDB).filter(UserDB.id == user_id).first()
    if user is None:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = updated_user.name
    user.age = updated_user.age
    session.commit()
    session.close()
    
    # Update CSV
    df = pd.read_sql("SELECT * FROM users", engine)
    df.to_csv('users.csv', index=False)
    
    return updated_user

# Delete a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    session = Session()
    user = session.query(UserDB).filter(UserDB.id == user_id).first()
    if user is None:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    session.close()
    
    # Update CSV
    df = pd.read_sql("SELECT * FROM users", engine)
    df.to_csv('users.csv', index=False)
    
    return {"message": f"User {user_id} deleted"}

# Download CSV endpoint
@app.get("/download/csv")
def download_csv():
    df = pd.read_sql("SELECT * FROM users", engine)
    df.to_csv('users.csv', index=False)
    return FileResponse('users.csv', media_type='text/csv', filename='users.csv')