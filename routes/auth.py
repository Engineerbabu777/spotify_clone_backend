import bcrypt
from pydatic_schemas.user_create import UserCreate
from database import get_db
from models.user import User
from fastapi import HTTPException,Depends
import uuid
from fastapi import APIRouter
from sqlalchemy.orm import Session
router = APIRouter()

@router.post("/signup")
def signup_user(user:UserCreate, db:Session = Depends(get_db)):

    user_db = db.query(User).filter(User.email == user.email).first()

    if user_db:
        raise HTTPException(400,'User with same email already exists')
    

    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(16))
    new_user = User(id=str(uuid.uuid4()),email=user.email,password=hashed_pw,name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
