from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # APP ECONOMY & TRUST ENGINE
    is_premium = Column(Boolean, default=False)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)

class Bookmaker(Base):
    __tablename__ = "bookmakers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class BookingCode(Base):
    __tablename__ = "booking_codes"

    id = Column(String, primary_key=True, default=generate_uuid)
    tipster_id = Column(String, ForeignKey("users.id"))
    bookmaker_id = Column(Integer, ForeignKey("bookmakers.id"))
    code_string = Column(String, nullable=False)
    total_odds = Column(Float, nullable=False)
    status = Column(String, default="PENDING") 
    
    # THE VIP WALL
    is_vip = Column(Boolean, default=False)