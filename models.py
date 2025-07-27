from sqlalchemy import Boolean, Column, ForeignKey,Integer, String, DATETIME, Date, func, Float, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String(255))

    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    timezone = Column(String(50), default="UTC")
    notification_preferences = Column(String(255), default="email,in_app")  # JSON-like string
    theme_preference = Column(String(20), default="light")  # light, dark, auto
    language = Column(String(10), default="en")
    
    created_at = Column(DATETIME, default=func.now())
    updated_at = Column(DATETIME, default=func.now(), onupdate=func.now())
    last_login = Column(DATETIME, default=func.now()) # deactivation of account if user is not active for three month

    todos = relationship("Todo", foreign_keys="Todo.owner_id", back_populates="owner", cascade="save-update") # those created by user
    asigned_todos = relationship("Todo", foreign_keys="Todo.asignee_id", back_populates="asignee", cascade="save-update")
    created_projects = relationship("Project", back_populates="owner", cascade="save-update") # those create by user
    created_teams = relationship("Team", back_populates="owner", cascade="save-update")

    # when user is deleted, remove it from teams and projects
    team_memberships = relationship("Team_Member", back_populates="member", cascade="all, delete-orphan")
    project_participations = relationship("Project_User", back_populates="participant", cascade="all, delete-orphan")

    @property
    def todos_count(self):
        return len(self.todos)
    

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    description = Column(Text, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asignee_id = Column(Integer,ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    status = Column(String(100), index= True, default="New")
    priority = Column(String(50), index = True, default="Low")
    type = Column(String(50), default="task", nullable=False)
    deleted = Column(Boolean, index=True, default=False)

    created_at = Column(DATETIME, index=True, default=func.now())
    updated_at = Column(DATETIME, index=True, default=func.now())
    deleted_at = Column(DATETIME, index=True, nullable=True)
    started_at = Column(Date, index=True, default=func.now(), nullable=True)
    finished_at = Column(Date, index=True, nullable= True)
    due_date = Column(Date, index=True)

    estimated_hours = Column(Float, nullable=True)
    actual_hours    = Column(Float, nullable=True)

    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), index = True, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"),index = True, nullable=True)

    owner = relationship("User", foreign_keys=[owner_id], back_populates="todos")
    asignee = relationship("User", foreign_keys=[asignee_id], back_populates="asigned_todos")
    project = relationship("Project", back_populates="todos")
    team = relationship("Team", back_populates="todos")
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if not self.due_date or self.status in ["completed", "cancelled"]:
            return False
        return self.due_date < func.current_date()
    
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    description = Column(Text, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    status = Column(String(100), index= True)
    color = Column(String(7), default="#3B82F6")
    deleted = Column(Boolean, index=True, default=False)

    created_at = Column(DATETIME, index=True, default=func.now())
    updated_at = Column(DATETIME, index=True, default=func.now())
    deleted_at = Column(DATETIME, index=True, nullable=True)
    started_at = Column(Date, index=True, default=func.now(), nullable=True)
    finished_at = Column(Date, index=True, nullable= True)
    due_date = Column(Date, index=True)

    estimated_hours = Column(Float, nullable=True)
    actual_hours    = Column(Float, nullable=True)
    budget          = Column(Float, nullable=True)
    currency        = Column(String(5), nullable=True, default="EUR")

    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), index=True, nullable=True)
    type = Column(String(50), default="personal", nullable=False)

    todos = relationship("Todo", back_populates="project", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="created_projects")
    team  = relationship("Team", back_populates="projects")
    project_participants = relationship("Project_User", back_populates="project", cascade="all, delete-orphan")

    @property
    def progress_percentage(self):
        """Calculate project progress based on completed todos"""
        if not self.todos:
            return 0
        completed = sum(1 for todo in self.todos if todo.status == "done")
        return int((completed / len(self.todos)) * 100)
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if not self.due_date or self.status in ["completed", "cancelled"]:
            return False
        return self.due_date < func.current_date()

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True, nullable=False)
    description = Column(Text, index=True, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DATETIME, index=True, default=func.now())
    deleted_at = Column(DATETIME, index=True, nullable=True)
    color = Column(String(7), default="#3B82F6")
    deleted = Column(Boolean, index=True, default=False)

    owner = relationship("User", back_populates="created_teams")
    projects = relationship("Project", back_populates="team", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="team", cascade="all, delete-orphan")
    members = relationship("Team_Member", back_populates="team", cascade="all, delete-orphan")

    @property
    def member_count(self):
        return len(self.members)

class Team_Member(Base):
    __tablename__ = "user_teams_relations"
    id = Column(Integer, primary_key=True, index = True)
    member_id = Column(Integer, ForeignKey("users.id"), index = True, nullable=False)
    member_role = Column(String(10), default="basic", index=True) # basic or admin for delegations
    team_id = Column(Integer, ForeignKey("teams.id"), index = True, nullable=False)
    joined_at = Column(DATETIME, default=func.now())

    team = relationship("Team", back_populates="members")
    member = relationship("User", back_populates="team_memberships")

class Project_User(Base):
    __tablename__ = "project_users_relations"
    id = Column(Integer, primary_key=True, index = True)
    project_id = Column(Integer, ForeignKey("projects.id"), index = True, nullable=False)
    participant_id = Column(Integer, ForeignKey("users.id"), index = True, nullable=False)
    participant = relationship("User", back_populates="project_participations")
    project = relationship("Project", back_populates="project_participants")


class Logs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index = True)

