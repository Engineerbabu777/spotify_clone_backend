import bcrypt
from pydatic_schemas.user_create import UserLogin, UserCreate
from database import get_db
from models.user import User
from fastapi import HTTPException,Depends,Header
import uuid
from fastapi import APIRouter
from sqlalchemy.orm import Session
import jwt

router = APIRouter()

@router.post("/signup", status_code=201)
def signup_user(user:UserCreate, db:Session = Depends(get_db)):

    user_db = db.query(User).filter(User.email == user.email).first()

    if user_db:
        raise HTTPException(400,'User with same email already exists')
    

    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(32))
    new_user = User(id=str(uuid.uuid4()),email=user.email,password=hashed_pw,name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def signin_user(user:UserLogin,db:Session = Depends(get_db)):
    # FIND USER!
    user_db = db.query(User).filter(User.email == user.email).first() 

    # IF NO USER EROR TROW!
    if not user_db:
        raise HTTPException(404,"User not found!")

    # IF USER VALIDATE CREDENTIALS!
    compare_pass = bcrypt.checkpw(user.password.encode(), user_db.password)

    # IF NO THROW ERROR!
    if not compare_pass:
        raise HTTPException(400,"Invalid credentials!")
    
    token = jwt.encode({'id':user_db.id}, 'password_key')

    # ELSE RETURN THE USER!
    return {'token':token, 'user':user_db}

@router.get("/")
def current_user_data(x_auth_token:str = Header(), db:Session=Depends(get_db)):
   try:
        # TOKEN FROM HEADER!
    if not x_auth_token:
        raise HTTPException(401,"No auth token, access denied")

    # DECODE TOKEN!
    verified_token = jwt.decode(x_auth_token, 'password_key', algorithms=['HS256'])

    if not verified_token:
        raise HTTPException(401, "Token verification failed, authorization error")

    # GET ID FROM TOKEN
    userId = verified_token.get("id")

    # GET DATA USER AND RETURN!
    user_db = db.query(User).filter(User.id == userId).first()

    if not user_db:
         raise HTTPException(404, "User not found")

    return {"user":user_db}
       
   except jwt.PyJWTError:
       raise HTTPException(401, "Token is not valid, authorization failed")
