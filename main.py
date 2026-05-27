from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

# Build the tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS SECURITY CLEARANCE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SECURITY SETUP ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- USER ENDPOINTS ---
@app.post("/register", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password  
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.UserResponse)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return user

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- BOOKING CODE ENGINE ---
@app.post("/bookmakers", response_model=schemas.BookmakerResponse)
def create_bookmaker(bookmaker: schemas.BookmakerCreate, db: Session = Depends(get_db)):
    new_bookmaker = models.Bookmaker(name=bookmaker.name)
    db.add(new_bookmaker)
    db.commit()
    db.refresh(new_bookmaker)
    return new_bookmaker

@app.post("/codes", response_model=schemas.CodeResponse)
def create_booking_code(code: schemas.CodeCreate, tipster_id: str, db: Session = Depends(get_db)):
    new_code = models.BookingCode(
        tipster_id=tipster_id,
        bookmaker_id=code.bookmaker_id,
        code_string=code.code_string,
        total_odds=code.total_odds,
        status="PENDING",
        is_vip=code.is_vip  # <-- THIS IS THE SWITCH THAT LOCKS THE WALL
    )
    db.add(new_code)
    db.commit()
    db.refresh(new_code)
    return new_code

@app.get("/codes", response_model=list[schemas.CodeResponse])
def get_active_codes(db: Session = Depends(get_db)):
    active_codes = db.query(models.BookingCode).filter(
        models.BookingCode.status.in_(["PENDING", "LIVE"])
    ).all()
    return active_codes

# --- ADMIN ENDPOINTS ---
@app.put("/admin/codes/{code_id}/status")
def update_code_status(code_id: str, new_status: str, db: Session = Depends(get_db)):
    code = db.query(models.BookingCode).filter(models.BookingCode.id == code_id).first()
    if not code:
        raise HTTPException(status_code=404, detail="Code not found")
    
    code.status = new_status.upper()
    
    if code.status in ["WON", "LOST"]:
        tipster = db.query(models.User).filter(models.User.id == code.tipster_id).first()
        if tipster:
            if code.status == "WON":
                tipster.total_wins += 1
            elif code.status == "LOST":
                tipster.total_losses += 1
                
    db.commit()
    db.refresh(code)
    return {"message": f"Code status updated to {code.status}", "tipster_stats_updated": True}
# --- FINANCIAL ENGINE (WEBHOOKS) ---
@app.post("/webhook/payfast")
def payfast_webhook(payment_data: schemas.PaymentWebhook, db: Session = Depends(get_db)):
    # 1. Check if the payment actually cleared the bank
    if payment_data.status.upper() != "COMPLETE":
        return {"message": "Payment not complete. No upgrade given."}
    
    # 2. Find the user who just paid
    user = db.query(models.User).filter(models.User.id == payment_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in vault")
    
    # 3. AUTOMATE THE CROWN 👑
    user.is_premium = True
    
    # 4. Save the upgraded status to the vault
    db.commit()
    db.refresh(user)
    
    return {"message": "Payment successful. User upgraded to Premium!"}