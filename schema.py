from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

class TodoBase(BaseModel):
    title          : str
    description    : Optional[str] = None
    status         : Optional[str] = None
    due_date       : Optional[date] = None
    started_at     : Optional[date] = None
    finished_at    : Optional[date] = None
    asignee_id     : Optional[int] = None
    priority       : Optional[str] = None
    team_id        : Optional[int] = None
    project_id     : Optional[int] = None
    type           : Optional[str] = "task"
    estimated_hours: Optional[float] = None
    actual_hours   : Optional[float] = None
    color          : Optional[str] = None

class TodoCreate(BaseModel):
    title          : str
    description    : Optional[str] = None
    status         : Optional[str] = None
    due_date       : Optional[date] = None
    started_at     : Optional[date] = None
    finished_at    : Optional[date] = None
    asignee_id     : Optional[int] = None
    priority       : Optional[str] = None
    team_id        : Optional[int] = None
    project_id     : Optional[int] = None
    type           : Optional[str] = "task"
    estimated_hours: Optional[float] = None
    actual_hours   : Optional[float] = None
    color          : Optional[str] = None

class TodoUpdate(TodoBase):
    title          : str
    description    : Optional[str] = None
    status         : Optional[str] = None
    due_date       : Optional[date] = None
    started_at     : Optional[date] = None
    finished_at    : Optional[date] = None
    asignee_id     : Optional[int] = None
    priority       : Optional[str] = None
    team_id        : Optional[int] = None
    project_id     : Optional[int] = None
    type           : Optional[str] = "task"
    estimated_hours: Optional[float] = None
    actual_hours   : Optional[float] = None
    color          : Optional[str] = None

class TodoDelete(BaseModel):
    delete         : bool
    deleted_at     : datetime
   
class Todo(TodoBase):
    id        : int
    owner_id  : int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode= True

class ProjectBase(BaseModel):
    title       : str
    description : Optional[str] = None
    status      : Optional[str] = None
    team_id     : Optional[int] = None
    type        : Optional[str] = "personal"
    color       : Optional[str] = "#3B82F6"

    due_date        : Optional[date] = None
    started_at      : Optional[date] = None
    finished_at     : Optional[date] = None
    estimated_hours : Optional[float] = None
    actual_hours    : Optional[float] = None
    budget          : Optional[float] = None
    currency        : Optional[str] = "EUR"

class ProjectCreate(BaseModel):
    title       : str
    description : Optional[str] = None
    status      : Optional[str] = None
    team_id     : Optional[int] = None
    type        : Optional[str] = "personal"
    color       : Optional[str] = "#3B82F6"

    due_date        : Optional[date] = None
    started_at      : Optional[date] = None
    finished_at     : Optional[date] = None
    estimated_hours : Optional[float] = None
    actual_hours    : Optional[float] = None
    budget          : Optional[float] = None
    currency        : Optional[str] = "EUR"


class ProjectUpdate(BaseModel):
    title      : str
    description : Optional[str] = None
    status      : Optional[str] = None
    team_id     : Optional[int] = None
    type        : Optional[str] = "personal"
    color       : Optional[str] = "#3B82F6"

    due_date        : Optional[date] = None
    started_at      : Optional[date] = None
    finished_at     : Optional[date] = None
    estimated_hours : Optional[float] = None
    actual_hours    : Optional[float] = None
    budget          : Optional[float] = None
    currency        : Optional[str] = "EUR"

class ProjectDelete(BaseModel):
    delete         : bool
    deleted_at     : datetime
   

class Project(ProjectBase):
    id          : int
    owner_id    : int
    created_at  : datetime
    updated_at  : datetime

    class Config:
        orm_mode= True

class ProjectUserBase(BaseModel):
    participant_id   : int
    project_id       : int

class ProjectUserCreate(ProjectUserBase):
    pass

class ProjectUser(ProjectUserBase):
    id: int
    class Config:
        orm_mode= True

class TeamBase(BaseModel):
    title       : str
    description : Optional[str] = None
    color       : Optional[str] = "#3B82F6"

class TeamCreate(BaseModel):
    title       : str
    description : Optional[str] = None
    color       : Optional[str] = "#3B82F6"

class TeamUpdate(BaseModel):
    title       : str
    description : Optional[str] = None
    color       : Optional[str] = "#3B82F6"

class TeamDelete(BaseModel):
    delete         : bool
    deleted_at     : datetime
   
class Team(TeamBase):
    id          : int
    owner_id    : int
    created_at  : datetime
    members     : List['User'] = []

    class Config:
        orm_mode= True

class TeamMemberBase(BaseModel):
    member_id  : int
    team_id    : int
    member_role : Optional[str] = "basic"

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMember(TeamMemberBase):
    id        : int
    joined_at : datetime
    class Config:
        orm_mode= True

class UserBase(BaseModel):
    email : EmailStr
    name  : str

class UserUpdate(BaseModel):
    name             : str
    is_active        : bool  # for deleted or not used accounts
    avatar_url       : Optional[str] = None
    bio              : Optional[str] = None
    timezone         : Optional[str] = "UTC"
    theme_preference : Optional[str] = "light"  # light, dark, auto
    language         : Optional[str] = "en"
    lastlogin        : datetime

class UserRegister(BaseModel):
    email    : EmailStr
    name     : str
    password : str

class UserLogin(BaseModel):
    email    : EmailStr
    password : str

class UserInDB(UserBase):
    id              : int
    hashed_password : str
    is_active       : bool = True

class User(UserBase):
    id                     : int
    is_active              : bool
    todos                  : List[Todo] = []
    asigned_todos          : List[Todo] = []
    timezone               : Optional[str] = "UTC"
    theme_preference       : Optional[str] = "light"  # light, dark, auto
    language               : Optional[str] = "en"

    class Config:
        orm_mode = True

Todo.update_forward_refs()
Project.update_forward_refs()
Team.update_forward_refs()
User.update_forward_refs()