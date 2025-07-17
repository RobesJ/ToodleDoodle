from pydantic import BaseModel, EmailStr
from typing import Optional, List

class TodoBase(BaseModel):
    title : str
    description : Optional[str] = None

class TodoCreate(TodoBase):
    title : str
    description : Optional[str] = None

class Todo(TodoBase):
    id : int
    owner_id : int

    class Config:
        orm_mode= True

class UserBase(BaseModel):
    email : EmailStr
    name : str

class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True

class User(UserBase):
    id : int
    is_active : bool
    todos : List[Todo] = []

    class Config:
        orm_mode = True