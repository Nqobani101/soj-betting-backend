import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Look for the Render Vault Key
RENDER_DB_URL = os.getenv("DATABASE_URL")

# 2. Make the engine smart
if RENDER_DB_URL:
    # Fix the Render prefix quirk
    if RENDER_DB_URL.startswith("postgres://"):
        RENDER_DB_URL = RENDER_DB_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = RENDER_DB_URL
else:
    # If no Render key is found, fall back to the local laptop database
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1995@localhost/postgres"

# The Engine handles the physical connection to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# The Session is what we use to actually talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all our database tables
Base = declarative_base()

# This is a dependency we will use later to give each web request its own database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()