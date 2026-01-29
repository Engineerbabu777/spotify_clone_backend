
from pydantic import BaseModel;

class UserCreate(BaseModel):
    name: str 
    email: str 
    password: str


class LoginUser(BaseModel):
    email: str
    password: str 