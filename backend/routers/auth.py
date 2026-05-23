from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import hashlib

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- DB dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Simple hash (use bcrypt in production) ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

# --- Schemas ---
class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="3–30 chars, letters/digits/underscores only"
    )
    email: EmailStr
    password: str = Field(min_length=8, max_length=64, description="Minimum 8 characters")

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=3, max_length=64)

# --- Routes ---
@router.post("/register", summary="Register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. Username and email must be unique."""
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken. Please choose a different one."
        )
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login", summary="Login")
async def login(request: Request, db: Session = Depends(get_db)):
    """Login with username and password."""
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/x-www-form-urlencoded" in content_type:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
    else:
        try:
            json_data = await request.json()
            username = json_data.get("username")
            password = json_data.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required."
        )

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
    return {
        "access_token": f"mock_token_{username}",
        "token_type": "bearer",
        "username": user.username,
        "email": user.email
    }

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    print(f"--- get_current_user DEBUG: token='{token}' ---")
    if not token or not token.startswith("mock_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    username = token.replace("mock_token_", "")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.get("/me", summary="Get Current User")
def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
