from pydantic import BaseModel
from typing import Optional

# --- USER BOUNCERS ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_premium: bool
    total_wins: int
    total_losses: int

    class Config:
        from_attributes = True

# The new Login Bouncer (Only pasted once!)
class UserLogin(BaseModel):
    email: str
    password: str

# --- BOOKMAKER BOUNCERS ---
class BookmakerCreate(BaseModel):
    name: str

class BookmakerResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# --- BOOKING CODE BOUNCERS ---
class CodeCreate(BaseModel):
    bookmaker_id: int
    code_string: str
    total_odds: float
    is_vip: bool

class CodeResponse(BaseModel):
    id: str
    tipster_id: str
    bookmaker_id: int
    code_string: str
    total_odds: float
    status: str
    is_vip: bool

    class Config:
        from_attributes = True
        
# --- FINANCIAL BOUNCERS ---
class PaymentWebhook(BaseModel):
    user_id: str
    amount_paid: float
    status: str