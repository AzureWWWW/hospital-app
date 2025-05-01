#includes routing logic

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from models.admin import Admin
from models.appointment import Appointment
from schemas.admin import DefaultAdminUpdateAdmin, RoleUpdate
from schemas.user import UserUpdate
from core.utils import get_current_admin, getValidUser

router = APIRouter()



def create_patient(patient_user_id: int, db: Session = Depends(get_db)):
    db_user =  getValidUser(patient_user_id, db)
    db_patient = Patient(user_id=patient_user_id)
    db.add(db_patient)
    db_user.role = "patient"
    db.commit()
    db.refresh(db_patient)
    db.refresh(db_user)
    return db_user

def create_doctor(doctor_user_id: int, db: Session = Depends(get_db)):
    db_user =  getValidUser(doctor_user_id, db)
    db_doctor = Doctor(user_id=doctor_user_id)
    db.add(db_doctor)
    db_user.role = "doctor"
    db.commit()
    db.refresh(db_doctor)
    db.refresh(db_user)
    return db_user

def create_admin(admin_user_id: int, db: Session = Depends(get_db)):
    db_user =  getValidUser(admin_user_id, db)
    db_admin = Admin(user_id=admin_user_id)
    db.add(db_admin)
    db_user.role = "admin"
    db.commit()
    db.refresh(db_admin)
    db.refresh(db_user)
    return db_user

@router.get("/getNonAssignedUsers/")
def getNonAssignedUsers( db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    user_data = db.query(User).filter(User.is_valid == 1, User.role == "user").all()
    result = []
    if not user_data:
        return result
    else:
        for user in user_data:
            if user.user_id == 1:
                continue
            else:
                info ={"user_id": user.user_id,
                    "full_name": str(user.first_name) + " " + str(user.last_name),
                    "username":user.username ,
                    "role": user.role}
                result.append(info)
    return result

@router.put("/updateRole/{user_id}", response_model=UserUpdate)
def update_user_role(
    user_id: int, 
    role_update: RoleUpdate, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(get_current_admin)):
    if user_id == 1:
        raise HTTPException(status_code=404, detail="Error: This is a Default Admin")
    roles = ['admin', 'doctor', 'patient', 'user']
    role_update.new_role = role_update.new_role.lower()
    if role_update.new_role not in roles:
        raise HTTPException(status_code=404, detail="Invalid Role")
    
    db_user =  getValidUser(user_id, db)
    if db_user.role != 'user':
        raise HTTPException(status_code=404, detail=f"You Can't Change To Another Role, User is a {db_user.role}")
    if db_user.role == role_update.new_role:
        raise HTTPException(status_code=404, detail=f"User is Already {db_user.role}")
    
    #set the status = false and status_expiry date in the corresponding table 
    if db_user.role == "patient":
        search_db = db.query(Patient).filter(Patient.user_id==user_id).all()
        for current_user in search_db:
            if current_user.is_patient == True:
                current_user.is_patient = False
                current_user.status_expiry = datetime.now(timezone.utc)
                db.add(current_user)
    elif db_user.role == "doctor":
        search_db = db.query(Doctor).filter(Doctor.user_id==user_id).all()
        for current_user in search_db:
            if current_user.is_doctor == True:
                current_user.is_doctor = False
                current_user.status_expiry = datetime.now(timezone.utc)
                db.add(current_user)
    elif db_user.role == "admin":
        search_db = db.query(Admin).filter(Admin.user_id==user_id).all()
        for current_user in search_db:
            if current_user.is_admin == True:
                current_user.is_admin = False
                current_user.status_expiry = datetime.now(timezone.utc)
                db.add(current_user)
    db.commit()
                
    #create a new entry in the corresponding table
    if role_update.new_role == "doctor":
        create_doctor(user_id, db)
    elif role_update.new_role == "patient":
        create_patient(user_id, db)
    elif role_update.new_role == "admin":
        create_admin(user_id, db)
        
    #update role in the user table
    db_user.role = role_update.new_role
    db.commit()
    db.refresh(db_user)
    return db_user

def get_admin_name_by_id(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id==admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin Not Found")
    user = db.query(User).filter(User.user_id == admin.user_id).first() 
    if not user:
        raise HTTPException(status_code=404, detail="Admin is Not a User")
    return  f"{user.first_name} {user.last_name}"

@router.get("/isDefaultAdmin/")
def isDefaultAdmin(current_admin: User = Depends(get_current_admin)):
    if current_admin.user_id ==1:
        return True
    return False
    


@router.put("/update_admin_status_expiry/")
def update_doctor_status_expiry(admin_id: int, admin_info: DefaultAdminUpdateAdmin, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    if admin_id ==1:
        raise HTTPException(status_code=404, detail="Default Admin Can't be Updated")
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin Not Found")
    
    if admin.status_expiry:
        raise HTTPException(status_code=404, detail="Status Expiry Can't be Changed")
    
    if admin_info.status_expiry <=  datetime.now(timezone.utc):
        admin.is_admin = 0
    admin.status_expiry = admin_info.status_expiry
    db.commit()
    db.refresh(admin)
    
    

@router.get("/getAllAdmins/")
def getAllAdmins(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    if current_admin.user_id == 1:    
        info = []
        admin_db = db.query(Admin).all()
        for admin in admin_db:
            admin_name = get_admin_name_by_id(admin.admin_id,db)
            user = db.query(User).filter(User.user_id == admin.user_id).first() 
            if not user:
                raise HTTPException(status_code=404, detail="User Not Found")
            app_data = {"admin_id": admin.admin_id,
                        "admin_name":admin_name,
                        "username":user.username,
                        "status_expiry": admin.status_expiry,
                        "email":user.email,
                        "phone_number": user.phone_number}
            info.append(app_data)
        return info
    raise HTTPException(status_code=404, detail=" Default Administrator Privileges are Needed")
