from sqlalchemy.orm import Session
from . import schema, models
from .utils.pwd_encryption import hash_pwd, verify_pwd

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip:int=0, limit:int=100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user:schema.UserRegister):
    hashed_password = hash_pwd(user.password)
    db_user = models.User(
        email= user.email, 
        name = user.name,
        hashed_password = hashed_password,
        is_active = True
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_pwd(password, user.hashed_password):
        return False
    return user

def get_todos(db: Session, user_id: int, skip: int=0, limit: int=100):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id).offset(skip).limit(limit).all()

def create_users_todo(db: Session, todo:schema.TodoCreate, user_id: int):
    db_todo = models.Todo(title = todo.title,
                          description = todo.description,
                          status = todo.status,
                          due_date = todo.due_date,
                          owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db:Session, todo_id: int, todo_to_update:schema.UpdateTodo, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id).first()

    if not db_todo:
        return None
    
    update_data = todo_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db:Session, todo_id: int, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id).first()

    if not db_todo:
        return None
    
    db.delete(db_todo)
    db.commit()
    return True