from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import bcrypt
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(64), nullable=False)

# SQLAlchemy connection to the database
engine = create_engine('postgresql://user:password@localhost/database')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Login request data model
class LoginData(BaseModel):
    username: str
    password: str

# Login endpoint
@app.post("/login")
def login(login_data: LoginData, db: SessionLocal = Depends(get_db)):
    # Get the user from the database
    user = db.query(User).filter(User.username == login_data.username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Check the password
    if not bcrypt.checkpw(login_data.password.encode(), user.password.encode()):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return JSONResponse(content={"message": "Login successful"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
