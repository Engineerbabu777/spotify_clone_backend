import fastapi
from fastapi import HTTPException, Header, Depends
import jwt
from models.user import User
from sqlalchemy.orm import Session
from database import get_db



def auth_middleware(x_auth_token:str = Header(), db:Session=Depends(get_db)):
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
      
       return {"token":x_auth_token, 'user_id':userId}
    
    except jwt.PyJWTError:
       raise HTTPException(401, "Token is not valid, authorization failed")

    