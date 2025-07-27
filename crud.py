from sqlalchemy.orm import Session
from . import schema, models
from .utils.pwd_encryption import hash_pwd, verify_pwd
from datetime import datetime

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
        is_active = True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db:Session, user_to_update:schema.UserUpdate, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        return None
    
    update_data = user_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db:Session, user_id: int, delegate: bool):
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.is_active == True).first()

    if not db_user:
        return None
    
    users_todos    =  db.query(models.Todo).filter(models.Todo.owner_id == user_id, models.Todo.deleted == False).all()
    users_projects =  db.query(models.Project).filter(models.Project.owner_id == user_id, models.Project.deleted == False).all()
    users_teams    =  db.query(models.Team).filter(models.Team.owner_id == user_id, models.Team.deleted == False).all()
    
    for todo in users_todos:
        if todo.type == "task":
            todo.deleted = True
            todo.deleted_at = datetime.now()
        elif todo.type == "team":
            if delegate:
                pass
                delegator = db.query(models.Team_Member).filter(models.Team_Member.team_id == todo.team_id, models.Team_Member.member_role == "admin").first()
                todo.owner_id = delegator.member_id
                todo.owner = delegator
            else:
                todo.deleted = True
                todo.deleted_at = datetime.now()
        elif todo.type == "project_team":
            if delegate:
                delegator =  db.query(models.Team_Member).filter(models.Team_Member.team_id == todo.team_id, models.Team_Member.member_role == "admin").first()
                todo.owner_id = delegator.member_id
                todo.owner = delegator
            else:
                todo.deleted = True
                todo.deleted_at = datetime.now()

    for project in users_projects:
        if project.type == "personal":
            project.deleted_at = datetime.now()
            project.deleted = True
        else:
            if delegate:
                pass
                delegator = db.query(models.Team_Member).filter(models.Team_Member.team_id == project.team_id, models.Team_Member.member_role == "admin").first()
                project.owner_id = delegator.member_id
                project.owner = delegator
            else:
                project.deleted_at = datetime.now()
                project.deleted = True

    for team in users_teams:
        if delegate:
            delegator = db.query(models.Team_Member).filter(models.Team_Member.team_id == team.team_id, models.Team_Member.member_role == "admin").first()
            team.owner_id = delegator.member_id
            team.owner = delegator
        else:
            team.deleted_at = datetime.now()
            team.deleted = True


    db_user.is_active = False
    db_user.last_login = datetime.now()

    db.commit()
    db.refresh(db_user)
    return True

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_pwd(password, user.hashed_password):
        return False
    return user

# get current users todos
def get_todos(db: Session, user_id: int, skip: int=0, limit: int=100):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id, models.Todo.deleted == False).offset(skip).limit(limit).all()

def create_users_todo(db: Session, todo:schema.TodoCreate, user_id: int):
    db_todo = models.Todo(
        title = todo.title,
        description = todo.description,
        status = todo.status,
        due_date = todo.due_date,
        owner_id= user_id,
        priority = todo.priority,
        estimated_hours = todo.estimated_hours,
        actual_hours    = todo.actual_hours,
        started_at = todo.started_at,
        finished_at = todo.finished_at,
        asignee_id = todo.asignee_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_users_todo(db:Session, todo_id: int, todo_to_update:schema.TodoUpdate, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id, models.Todo.deleted == False).first()

    if not db_todo:
        return None
    
    update_data = todo_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db:Session, todo_id: int, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id, models.Todo.deleted == False).first()

    if not db_todo:
        return None
    
    db_todo.deleted = True
    db_todo.deleted_at = datetime.now()

    db.commit()
    db.refresh(db_todo)
    return True

def get_personal_projects(db: Session, user_id: int, skip: int=0, limit: int=100):
    return db.query(models.Project).filter(models.Project.owner_id == user_id, models.Project.deleted == False).offset(skip).limit(limit).all()

def create_personal_project(db:Session, project: schema.ProjectCreate, user_id: int):
    db_project = models.Project(
        title = project.title,
        description = project.description,
        status = project.status,
        due_date = project.due_date,
        owner_id= user_id,
        estimated_hours = project.estimated_hours,
        actual_hours    = project.actual_hours,
        currency = project.currency,
        budget = project.budget,
        color = project.color,
        started_at = project.started_at,
        finished_at = project.finished_at
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_personal_project(db:Session, project_id: int, project_to_update: schema.ProjectUpdate, user_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == user_id, models.Project.deleted == False).first()

    if not db_project:
        return None
    
    update_data = project_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_personal_project(db:Session, project_id: int, user_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == user_id, models.Project.deleted == False).first()
    if not db_project:
        return None
    
    db_todos   = db.query(models.Todo).filter(models.Todo.project_id == project_id, models.Todo.owner_id == user_id, models.Todo.deleted == False).all()
    for todo in db_todos:
        todo.deleted = True
        todo.deleted_at = datetime.now()

    db_project.deleted = True
    db_project.deleted_at = datetime.now()
    
    db.commit()
    db.refresh(db_project)
    return True

# get todos on project created by current user
def get_todos_on_personal_project(db: Session, user_id: int, project_id: int, skip: int=0, limit: int=100):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id, models.Todo.project_id == project_id, models.Todo.deleted == False).offset(skip).limit(limit).all()

def create_personal_projects_todo(db: Session, todo:schema.TodoCreate, user_id: int, project_id: int):
    db_todo = models.Todo(
        title = todo.title,
        description = todo.description,
        status = todo.status,
        due_date = todo.due_date,
        owner_id= user_id,
        priority = todo.priority,
        project_id = project_id,
        type = "project",
        estimated_hours = todo.estimated_hours,
        actual_hours    = todo.actual_hours,
        started_at = todo.started_at,
        finished_at = todo.finished_at,
        asignee_id = todo.asignee_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_personal_projects_todo(db:Session, todo_id: int, project_id: int,  todo_to_update:schema.TodoUpdate, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id, models.Todo.deleted == False, models.Todo.project_id == project_id).first()

    if not db_todo:
        return None
    
    update_data = todo_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

def create_team(db:Session, user_id: int, team: schema.TeamCreate, members_id: list[int]):
    member_list = []
    for id in members_id:
        member_list.append(db.query(models.User).filter(models.User.id == id).first())

    db_team = models.Team(
        title= team.title,
        description=team.description,
        owner_id=user_id
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)

    if db_team:
        for id in members_id:
            db_user_team_relation = models.Team_Member(member_id= id,
                                                       team_id = db_team.id)
            db.add(db_user_team_relation)
            db.commit()
            db.refresh(db_user_team_relation)
    return db_team

def update_team(db: Session, team_id: int, team_to_update: schema.TeamUpdate):
    db_team = db.query(models.Team).filter(models.Team.id == team_id, models.Team.deleted == False).first()

    if not db_team:
        return None
    
    update_data = team_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_team, field, value)
    
    db.commit()
    db.refresh(db_team)
    return db_team

def get_teams_by_owner(db: Session, user_id: int, skip: int=0, limit: int=100):
    return db.query(models.Team).filter(models.Team.owner_id == user_id, models.Team.deleted == False).offset(skip).limit(limit).all()

def get_teams_by_membership(db: Session, user_id: int, skip: int=0, limit: int=100):
    return db.query(models.Team_Member).filter(models.Team_Member.member_id == user_id, models.Team.deleted == False).offset(skip).limit(limit).all()

def create_team_project(db:Session, project: schema.ProjectCreate, user_id: int, team_id: int):
    db_project = models.Project(
        title = project.title,
        description = project.description,
        status = project.status,
        due_date = project.due_date,
        owner_id= user_id,
        team_id = team_id,
        type = "team",
        estimated_hours = project.estimated_hours,
        actual_hours    = project.actual_hours,
        currency = project.currency,
        budget = project.budget,
        color = project.color,
        started_at = project.started_at,
        finished_at = project.finished_at
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_team_project(db: Session, team_id: int, user_id: int, project_id: int,  project_to_update: schema.ProjectUpdate):
    db_project = db.query(models.Project).filter(models.Project.team_id == team_id, models.Project.id == project_id, models.Project.deleted == False, models.Project.owner_id == user_id).first()

    if not db_project:
        return None
    
    update_data = project_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def create_team_todo(db:Session, user_id: int, team_id: int, todo: schema.TodoCreate):
    db_todo = models.Todo(
        title = todo.title,
        description = todo.description,
        status = todo.status,
        due_date = todo.due_date,
        owner_id= user_id,
        team_id= team_id,
        priority = todo.priority,
        type = "team",
        estimated_hours = todo.estimated_hours,
        actual_hours    = todo.actual_hours,
        started_at = todo.started_at,
        finished_at = todo.finished_at,
        asignee_id = todo.asignee_id
    )
    
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_team_todo(db: Session, team_id: int, todo_id:int, user_id: int, todo_to_update: schema.TodoUpdate):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id, models.Todo.team_id == team_id, models.Todo.deleted == False).first()

    if not db_todo:
        return None
    
    update_data = todo_to_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

def create_team_todo_in_team_project(db:Session, user_id: int, team_id: int, project_id: int, todo: schema.TodoCreate):
    db_todo = models.Todo(
        title = todo.title,
        description = todo.description,
        status = todo.status,
        due_date = todo.due_date,
        owner_id= user_id,
        team_id= team_id,
        project_id = project_id,
        priority = todo.priority,
        type = "project_team",
        estimated_hours = todo.estimated_hours,
        actual_hours    = todo.actual_hours,
        started_at = todo.started_at,
        finished_at = todo.finished_at,
        asignee_id = todo.asignee_id
    )
    
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_team_todo_in_team_project(db: Session, team_id: int, todo_id:int, project_id: int, user_id: int, todo_to_update: schema.TodoUpdate):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id, models.Todo.team_id == team_id, models.Todo.project_id == project_id, models.Todo.deleted == False).first()

    if not db_todo:
        return None
    
    update_data = todo_to_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_team(db: Session, user_id: int, team_id: int, skip: 0, limit: 100):
    team_to_delete = db.query(models.Team).filter(models.Team.id == team_id, models.Team.deleted == False).first()

    if not team_to_delete or team_to_delete.owner_id != user_id:
        return None
    
    todos_to_delete    = db.query(models.Todo).filter(models.Todo.team_id == team_id, models.Todo.deleted == False).offset(skip).limit(limit).all()
    projects_to_delete = db.query(models.Project).filter(models.Project.team_id == team_id, models.Project.deleted == False).offset(skip).limit(limit).all()

    for todo in todos_to_delete:
       todo.deleted = True
       todo.deleted_at = datetime.now()
    
    for project in projects_to_delete:
       project.deleted = True
       project.deleted_at = datetime.now()
    
    team_to_delete.deleted = True
    team_to_delete.deleted_at = datetime.now()

    db.commit()
    db.refresh(team_to_delete)
    return "team was deleted"

def add_team_members(db: Session, user_id: int, team_id: int):
    user_to_add = models.Team_Member(
        team_id = team_id,
        member_id = user_id
    )
    db.add(user_to_add)
    db.commit()
    db.refresh(user_to_add)
    return user_to_add

def remove_team_members(db: Session, user_id: int, team_id: int,):
    member_to_remove = db.query(models.Team_Member).filter(models.Team_Member.member_id == user_id, models.Team_Member.team_id == team_id).first()
    if not member_to_remove:
        return None
    
    db.delete(member_to_remove)
    db.commit()
    return "User was removed from team"

def add_project_participants(db: Session, user_id: int, project_id: int):
    user_to_add = models.Project_User(
        project_id = project_id,
        participant_id = user_id
    )
    db.add(user_to_add)
    db.commit()
    db.refresh(user_to_add)
    return user_to_add

def remove_project_participants(db: Session, user_id: int, project_id: int):
    participant_to_delete = db.query(models.Project_User).filter(models.Project_User.participant_id == user_id, models.Project_User.project_id == project_id).first()
    if not participant_to_delete:
        return None
    
    db.delete(participant_to_delete)
    db.commit()
    return "User was removed from project"
