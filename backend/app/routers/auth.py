from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import create_access_token, hash_password, verify_password
from ..database import get_db, next_id, public_doc, utcnow
from ..dependencies import get_current_user
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db = Depends(get_db)):
    email = payload.email.lower()
    existing = db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = dict(
        id=next_id(db, "users"),
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        created_at=utcnow(),
    )
    db.users.insert_one(user)
    return TokenOut(access_token=create_access_token(user["id"]), user=UserOut(**public_doc(user)))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db = Depends(get_db)):
    user = db.users.find_one({"email": payload.email.lower()})
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenOut(access_token=create_access_token(user["id"]), user=UserOut(**public_doc(user)))


@router.get("/me", response_model=UserOut)
def me(current = Depends(get_current_user)):
    return current
