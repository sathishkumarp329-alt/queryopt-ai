import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

os.makedirs(os.path.dirname(os.path.abspath(settings.APP_DB_PATH)), exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.APP_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_app_db():
    from backend.models import db_models
    Base.metadata.create_all(bind=engine)
