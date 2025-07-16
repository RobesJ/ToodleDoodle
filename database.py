from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@localhost:port/YOUR_DATABASE
URL_DATABASE = os.getenv("DATABASE_URL")
engine = create_engine(URL_DATABASE, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base= declarative_base()