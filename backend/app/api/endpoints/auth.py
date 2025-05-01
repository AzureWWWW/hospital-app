from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer

from models.user import User
from models.tokenBlacklist import TokenBlacklist

from schemas.user import UserCreate
from schemas.token import Token
from core.security import hash_password, create_access_token, decode_token, decode_expired_token 
from core.config import settings
from core.utils import authenticate_user, get_current_user, isNameValid, isEmailValid, isPhoneNumberValid 
from database import get_db
from datetime import datetime, timedelta

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register/")
def register(userData: UserCreate, db: Session = Depends(get_db)):
    # check if username, email already exists
    existing_user = db.query(User).filter(User.username == userData.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="This Username Has Already Been Used")
    existed_email = db.query(User).filter(User.email == userData.email).first()
    if existed_email:
        raise HTTPException(status_code=400, detail="This Email Has Already Been Used")
    
    hashed_password = hash_password(userData.password)
    if userData.first_name and userData.last_name:
        name = userData.first_name + ' '+ userData.last_name
        if isNameValid(name):
            if  isEmailValid(userData.email) and isPhoneNumberValid(userData.phone_number):
                # create new user object
                db_user = User(
                    first_name=userData.first_name,
                    last_name=userData.last_name,
                    username=userData.username, 
                    email=userData.email, 
                    hashed_password=hashed_password,
                    phone_number=userData.phone_number,
                    role = "user"
                )
                        # add new user to database
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                return {"message": "User Registered Successfully"}
            #exceptions are raised within these functions
        else:
            raise HTTPException(status_code=400, detail="Invalid Name")

    raise HTTPException(status_code=400, detail="Incomplete Name")
   

    
# User login and return token
@router.post("/login/")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
    ) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/logout/")
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    decoded_token = verify_token(token, db)
    if decoded_token:
        # Blacklist token 
        blacklist_db = TokenBlacklist(access_token = token, expired_at = datetime.utcnow() )
        db.add(blacklist_db)
        db.commit()
        db.refresh(blacklist_db)
        return {"msg": "DONE"}

@router.post("/setTokenToExpired/")
def setTokenToExpired(token: str = Query(...), db: Session = Depends(get_db)):
    blacklist_token = db.query(TokenBlacklist).filter(TokenBlacklist.access_token == token).first()
    if blacklist_token:
        return {"msg": "Already Logged Out"}
    else:
        try:
            # check the encoded token is the right one
            decoded_token = decode_expired_token(token)
            if decoded_token:
                # Blacklist token 
                blacklist_db = TokenBlacklist(access_token =token, expired_at = datetime.utcnow() )
                db.add(blacklist_db)
                db.commit()
                db.refresh(blacklist_db)
                return {"msg": "DONE"}
            else:
                print("COULD NOT DECODE TOKEN\n")
        except:
            raise HTTPException(status_code=401, detail="Invalid Token")
    
    
def verify_token(token : str, db: Session = Depends(get_db)):
    #search for token in the blacklist_token table
    blacklist_token = db.query(TokenBlacklist).filter(TokenBlacklist.access_token == token).first()
    if blacklist_token:
        raise HTTPException(status_code=401, detail="User is Already Logged Out")
    else:
        try:
            # check the encoded token is the right one
            return decode_token(token)
        except:
            raise HTTPException(status_code=401, detail="Invalid Token")
        
