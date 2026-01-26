

from fastapi import FastAPI,HTTPException;
from pydantic import BaseModel;
from sqlalchemy import create_engine,Column,TEXT,VARCHAR,LargeBinary
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid 
import bcrypt

app = FastAPI()

DATABASE_URL = "postgresql://postgres:POSTGRESQL%40123%2E@localhost:5432/flutter_music_app"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

db = SessionLocal()


class UserCreate(BaseModel):
    name: str 
    email: str 
    password: str

Base = declarative_base()  
class User(Base):
    __tablename__ = 'users'
    
    id = Column(TEXT,primary_key=True)
    name = Column(VARCHAR(100))
    email = Column(VARCHAR(100))
    password = Column(LargeBinary)



@app.post("/signup")
def signup_user(user:UserCreate):

    user_db = db.query(User).filter(User.email == user.email).first()

    if user_db:
        raise HTTPException(400,'User with same email already exists')
    

    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(16))
    new_user = User(id=str(uuid.uuid4()),email=user.email,password=hashed_pw,name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user




@app.post("/signin")
def signin_user():

    pass

 

Base.metadata.create_all(engine)

