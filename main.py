'''
@app.delete("/students/delete/{student_id}")
async def delete_student(student_id: int):
    if student_id not in students:
        return {"Error" : "Student with this id does not exist"}
    del students[student_id]
    return {"Info" : f"Student with id {student_id} was deleted"}

'''

from . import crud, models, schema
from .database import SessionLocal, engine
from fastapi import FastAPI, Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from .utils.auth import *
from .utils.pwd_encryption import *
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Dependency
def get_db():
    db = SessionLocal()
    try : 
        yield db
    finally:
        db.close()

security = HTTPBearer()

@app.post("/register",response_model=schema.User)
def post_user(user:schema.UserRegister, db:Session=Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    return crud.create_user(db=db,user=user)

@app.post("/login")
def login_user(user: schema.UserLogin, db:Session = Depends(get_db)):
    authenticated_user = crud.authenticate_user(db, user.email, user.password)

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = signJWT(authenticated_user.email)
    return {
        **token,
        "user" : {
            "id": authenticated_user.id,
            "name": authenticated_user.name,
            "email": authenticated_user.email,
            "is_active": authenticated_user.is_active
        }
    }

@app.get("/users/me", response_model=schema.User)
def get_current_user_profile(current_user: models.User = Depends(get_current_user)):
    """Get current user's profile - JWT AUTHENTICATION REQUIRED"""
    return schema.User.from_orm(current_user)

@app.get("/users/", response_model=list[schema.User])
def get_users(skip:int=0, limit:int=0, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    users = crud.get_users(db,skip=skip,limit=limit)
    return users

@app.get("/users/{user_id}/",response_model=schema.User)
def get_user(user_id:int, db:Session=Depends(get_db)):
    db_user = crud.get_user(db,user_id =user_id )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# get todos of one user
@app.get("/users/{user_id}/todos/", response_model=list[schema.Todo])
def get_todos(user_id: int, skip:int=0,limit:int=100,db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    todos = crud.get_todos(db, user_id= user_id, skip= skip,limit= limit)
    return todos

# create todo
@app.post("/users/{user_id}/add-todo/",response_model=schema.Todo)
def create_todo(user_id:int, todo:schema.TodoCreate, db:Session=Depends(get_db)):
    return crud.create_users_todo(db = db, user_id = user_id, todo = todo)


@app.put("/users/{user_id}/todos/{todo_id}", response_model=schema.Todo)
def update_todo(user_id: int, todo_id: int, todo:schema.UpdateTodo, db:Session=Depends(get_db)):
    updated_todo = crud.update_todo(db = db, todo_id = todo_id, user_id = user_id, todo_to_update = todo)

    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you dont have permission to modify it"
        )
    return updated_todo