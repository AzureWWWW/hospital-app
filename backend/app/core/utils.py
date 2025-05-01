# Common helper functions

# from datetime import datetime
# from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt


from core.security import verify_password, oauth2_scheme

from database import get_db
from models.user import User
from models.patient import Patient
from models.admin import Admin
from models.doctor import Doctor
from models.tokenBlacklist import TokenBlacklist
from core.config import settings
from schemas.token import TokenData
import re



# Get user from database using username as input
def get_user(username: str, db: Session):
    user = db.query(User).filter(User.username == username, User.is_valid == 1).first()   
    
    return user     

# authenticate user
def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username, db)
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_valid:       # check if user is deleted or not
        return False
    return user
   

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # verify token
    try:
        if isLoggedOut(token, db):
            raise HTTPException(status_code=400, detail="Authentication is Needed")
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        token_exp = payload.get("exp")
        if datetime.utcnow().timestamp() > token_exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired Session",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    

    user = db.query(User).filter(User.user_id==token_data.user_id).first()

    if user is None:
        raise credentials_exception
    return user

# # get current active user/ valid user
# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if not current_user.is_valid:
#         raise HTTPException(status_code=400, detail="Inactive User")
#     return current_user

# Admin role check
async def get_default_admin(db: Session = Depends(get_db)):
    default_admin = db.query(User).filter(User.user_id == 1).first()
    if not default_admin:
        raise HTTPException(status_code=403, detail="Default Admin is Missing")
    return default_admin 
     
def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator Access Required")
    return current_user


              
              
def Is_User_Valid(id, table, db):
    if table == "patient":
        db_search = db.query(Patient).filter(Patient.patient_id==id).first()
        if db_search is None:
            return False
        elif db_search.is_patient == True:
            return True
        return False
    elif table == "admin":
        db_search = db.query(Admin).filter(Admin.admin_id==id).first()
        if db_search is None:
            return False
        elif db_search.is_admin == True:
            return True
        return False
    elif table == "doctor":
        db_search = db.query(Doctor).filter(Doctor.doctor_id==id).first()
        if db_search is None:
            return False
        elif db_search.is_doctor == True:
            return True
        return False
    elif table == "user":
        db_search = db.query(User).filter(User.user_id==id).first()
        if db_search is None:
            return False
        elif db_search.is_valid == True:
            return True
        return False
    else:
        raise HTTPException(status_code=404, detail="Inexistant Table")

def isLoggedOut (token: str, db: Session = Depends(get_db)):
    db_search = db.query(TokenBlacklist).filter(TokenBlacklist.access_token==token).first()
    if db_search is None:
        return False
    return True
    
    
def getValidUser(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.user_id==user_id).all()
    for current_user in user_db:
        if current_user.is_valid == True:
            return current_user
    raise HTTPException(status_code=404, detail="User Not Found")

def isNameValid(name: str):
    
    if len(name.split(' ')) == 2 :
        if name.split(' ')[0].isalpha() and name.split(' ')[1].isalpha() :
            return True
    raise HTTPException(status_code=400, detail="Invalid Name")

def isEmailValid(email: str):
    if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return True
    raise HTTPException(status_code=400, detail="Invalid Email")

def isPhoneNumberValid(number: str):
    number = number.replace(" ", "")
    if len(number)<10 or len(number)>= 15:
        raise HTTPException(status_code=400, detail="Invalid Phone Number")
    else:
        if re.match(r'^\+\d{1,3}\d{8,14}$',number):
            return True
    raise HTTPException(status_code=400, detail="Invalid Phone Number")