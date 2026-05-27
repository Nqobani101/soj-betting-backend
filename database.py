from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# THE CONNECTION STRING (The "Keys" to the Vault)
# Format: postgresql://username:password@localhost/databasename
# You need to replace 'your_password_here' and 'your_database_name'
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1995@localhost/postgres"

# The Engine handles the physical connection to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# The Session is what we use to actually talk to the database (add users, read codes)
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