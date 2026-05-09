import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv

dotenv.load_dotenv()

DB_USER = os.getenv("CATALOG_DB_USER", os.getenv("POSTGRES_USER", "postgres"))
DB_PASSWORD = os.getenv("CATALOG_DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "postgres"))
DB_HOST = os.getenv("CATALOG_DB_HOST", os.getenv("POSTGRES_HOST", "catalog-db"))
DB_PORT = os.getenv("CATALOG_DB_PORT", os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("CATALOG_DB_NAME", os.getenv("POSTGRES_DB", "catalog_db"))

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
