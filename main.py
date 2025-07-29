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

def ensure_ownership(current_user: models.User, user_id: int):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail= "You are not authorized for this kind of action"
        )

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
    ensure_ownership(current_user= current_user, user_id= user_id)
    todos = crud.get_todos(db, user_id= user_id, skip= skip,limit= limit)
    return todos

# create users todo
@app.post("/users/{user_id}/add-todo/",response_model=schema.Todo)
def create_todo(user_id:int, todo:schema.TodoCreate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user= current_user, user_id= user_id)
    return crud.create_users_todo(db = db, user_id = user_id, todo = todo)


@app.put("/users/{user_id}/todos/{todo_id}", response_model=schema.Todo)
def update_todo(user_id: int, todo_id: int, todo:schema.TodoUpdate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user= current_user, user_id= user_id)
    updated_todo = crud.update_users_todo(db = db, todo_id = todo_id, user_id = user_id, todo_to_update = todo)

    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you dont have permission to modify it"
        )
    return updated_todo

@app.delete("/users/{user_id}/todos/{todo_id}")
def delete_todo(user_id: int, todo_id: int, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user= current_user, user_id= user_id)
    deletion = crud.delete_todo(db = db, todo_id = todo_id, user_id = user_id)

    if  not deletion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you don't have permission to delete it"
        )

    return {"message": "Todo deleted successfully"}


# get all personal projects
@app.get("/users/{user_id}/projects/", response_model=list[schema.Project])
def get_personal_projects(user_id: int, skip:int=0,limit:int=100, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user= current_user, user_id= user_id)
    projects = crud.get_personal_projects(db, user_id= user_id, skip= skip,limit= limit)
    return projects

# create personal project
@app.post("/users/{user_id}/add-project/",response_model=schema.Project)
def create_personal_project(user_id:int, project:schema.ProjectCreate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user= current_user, user_id= user_id)
    return crud.create_personal_project(db = db, user_id = user_id, project = project)

@app.put("/users/{user_id}/projects/{project_id}/", response_model=schema.Project)
def update_personal_project(user_id: int, project_id: int, project:schema.ProjectUpdate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    updated_project = crud.update_personal_project(db = db,  user_id = user_id, project_id = project_id, project = project)

    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you dont have permission to modify it"
        )
    return updated_project

# create users todo
@app.post("/users/{user_id}/projects/{project_id}/add-todo/",response_model=schema.Todo)
def create_personal_projects_todo(user_id: int, project_id: int,  todo:schema.TodoCreate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    return crud.create_personal_projects_todo(db = db, user_id = user_id, project_id = project_id, todo = todo)


@app.put("/users/{user_id}/projects/{project_id}/todos/{todo_id}", response_model=schema.Todo)
def update_projects_todo(user_id: int, todo_id: int, project_id: int, todo:schema.TodoUpdate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    updated_todo = crud.update_personal_projects_todo(db = db, todo_id = todo_id, user_id = user_id, project_id = project_id, todo_to_update = todo)

    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you dont have permission to modify it"
        )
    return updated_todo



# create personal project
@app.post("/users/{user_id}/add-team/",response_model=schema.Team)
def create_team(user_id:int, team:schema.TeamCreate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    return crud.create_team(db = db, user_id = user_id, team = team)
        

@app.post("/users/{user_id}/teams/{team_id}/add-project", response_model=schema.Project)
def create_team_project(user_id: int, team_id: int, project: schema.ProjectCreate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    return crud.create_team_project(db = db, user_id = user_id, team_id =  team_id, project=project)
       

@app.post("/users/{user_id}/teams/{team_id}/project/{project_id}/add-todo", response_model=schema.Todo)
def create_todo_in_team_project(user_id: int, team_id: int, project_id: int, todo: schema.TodoCreate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    return crud.create_team_todo_in_team_project(db = db, user_id = user_id, team_id = team_id, project_id = project_id, todo = todo),
        

@app.post("/users/{user_id}/teams/{team_id}/add-todo", response_model=schema.Todo)
def create_todo_in_team(user_id: int, team_id: int, todo: schema.TodoCreate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    return crud.create_team_todo(db = db, user_id = user_id, team_id = team_id, todo = todo)
        

@app.put("/users/{user_id}/teams/{team_id}")
def update_team(user_id: int, team_id: int, team: schema.TeamUpdate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    updated_team = crud.update_team(db = db,  user_id = user_id, team_to_update = team, team_id = team_id)

    if not updated_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found or you dont have permission to modify it"
        )
    return updated_team

@app.put("/users/{user_id}/teams/{team_id}/project/{project_id}", response_model=schema.Project)
def update_team_project(user_id: int, team_id: int, project_id: int, project: schema.ProjectUpdate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    updated_project = crud.update_team_project(db = db,  user_id = user_id, project_to_update = project, team_id = team_id, project_id = project_id)

    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you dont have permission to modify it"
        )
    return updated_project

@app.put("/users/{user_id}/teams/{team_id}/project/{project_id}/todos/{todo_id}", response_model=schema.Todo)
def update_todo_in_team_project(user_id: int, team_id: int, project_id: int, todo_id: int, todo: schema.TodoUpdate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    updated_todo = crud.update_team_todo_in_team_project(db = db, todo_id = todo_id, user_id = user_id, todo_to_update = todo, team_id = team_id, project_id = project_id)

    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you dont have permission to modify it"
        )
    return updated_todo
    

@app.put("/users/{user_id}/teams/{team_id}/todos/{todo_id}", response_model=schema.Todo)
def update_todo_in_team(user_id: int, team_id: int, todo_id: int, todo: schema.TodoUpdate, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    updated_todo = crud.update_team_todo(db = db, todo_id = todo_id, user_id = user_id, todo_to_update = todo, team_id = team_id)

    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you dont have permission to modify it"
        )
    return updated_todo

@app.delete("/users/{user_id}/teams/{team_id}")
def delete_team(user_id: int, team_id: int, skip: int, limit: int, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    removing = crud.delete_team(db = db, user_id = user_id, team_id= team_id, skip = skip, limit = limit)

    if  not removing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or you don't have permission to remove users"
        )

    return {"message": "Team deleted successfully"}

@app.post("/users/{user_id}/teams/{team_id}/add-member/{member_id}")
def add_team_member(user_id: int, team_id: int, member_id: int, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    success = crud.add_team_members(db =db, user_id=user_id, team_id=team_id, member_id= member_id)
    if  not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or you don't have permission to modifz team membership"
        )

    return {"message": "User added successfully to team"}

@app.post("/users/{user_id}/project/{project_id}/add-participant/{participant_id}")
def add_project_participant(user_id: int, project_id: int, participant_id: int, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    success = crud.add_project_participants(db = db, user_id= user_id, project_id=project_id, participant_id=participant_id)
    if  not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or you don't have permission to modify project"
        )

    return {"message": "User added successfully to project"}

@app.delete("/users/{user_id}/teams/{team_id}/remove-member/{member_id}")
def remove_team_member(user_id: int, team_id: int, member_id: int, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    removing = crud.remove_team_members(db = db, user_id = user_id, team_id= team_id, member_id=member_id)

    if  not removing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team or user not found or you don't have permission to remove users"
        )

    return {"message": "User was removed from team successfully"}

@app.delete("/users/{user_id}/project/{project_id}/add-participant/{participant_id}")
def remove_project_participant(user_id: int, project_id: int, participant_id: int, db:Session=Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_ownership(current_user=current_user, user_id=user_id)
    removing = crud.remove_project_participants(db = db, user_id = user_id, project_id = project_id, participant_id= participant_id)

    if  not removing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project or user to remove not found or you don't have permission to remove users"
        )

    return {"message": "User was removed from project successfully"}