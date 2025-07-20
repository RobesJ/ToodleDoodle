from sqlalchemy import Boolean, Column, ForeignKey,Integer, String, DATETIME, Date, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    todos = relationship("Todo", back_populates="owner")
    is_active = Column(Boolean, default=False)
    hashed_password = Column(String(255))

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    description = Column(String(255), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(100), index= True)
    created_at = Column(DATETIME, index=True, default=func.now())
    due_date = Column(Date, index=True)

    owner = relationship("User", back_populates="todos")
