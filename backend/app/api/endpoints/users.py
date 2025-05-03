
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from models.admin import Admin
from schemas.user import UserUpdate 
from .appointments import deactivate_appointment, get_user_appointments_by_user_id
from core.utils import get_current_admin, get_valid_user, is_email_valid, is_phone_number_valid, get_current_user, get_default_admin
from database import SessionLocal
from core.messages import invalid_doctor_specialty, user_not_found , default_admin_update , general_privileges_update 

router = APIRouter()

allowed_specialties = [
    "GENERAL","ANESTHESIOLOGY", "CARDIOLOGY", "DERMATOLOGY",
    "ENDOCRINOLOGY","GASTROENTEROLOGY","HEMATOLOGY","INFECTIOUS DISEASE",
    "INTERNAL MEDICINE", "NEPHROLOGY", "NEUROLOGY","OBSTETRICS AND GYNECOLOGY",
    "ONCOLOGY", "OPHTHALMOLOGY", "ORTHOPEDIC SURGERY", "PEDIATRICS",
    "PLASTIC SURGERY", "PSYCHIATRY","PULMONOLOGY", "RADIOLOGY",
    "RHEUMATOLOGY","SURGERY (GENERAL SURGERY)","THORACIC SURGERY",
    "UROLOGY","VASCULAR SURGERY","DENTISTRY","ALLERGY AND IMMUNOLOGY"
]



# remove users with expired status
def deactivate_expired_users(current_admin: User = Depends(get_default_admin)):
    db = SessionLocal()
    date_today = datetime.now()
    users = db.query(User).filter(User.is_valid == 1).all()
    for user in users:
        patient_data = None
        doctor_data = None
        admin_data = None
        if user.role =="patient":
            patient_data = db.query(Patient).filter(Patient.user_id == user.user_id, Patient.status_expiry <= date_today).first()
        elif user.role == "doctor":
            doctor_data = db.query(Doctor).filter(Doctor.user_id == user.user_id, Doctor.status_expiry <= date_today).first()
        elif user.role == "admin":
            admin_data = db.query(Admin).filter(Admin.user_id == user.user_id, Admin.status_expiry <= date_today).first()
        if patient_data or  doctor_data or admin_data:
            deactivate_user(user.user_id, db)            
    db.close()        

# Deactivate a user
@router.delete("/deactivate/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)):
    if user_id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= default_admin_update )
    user =  get_valid_user(user_id, db)
    
    # set user_status to invalid and status_expiry date: 
    if user.role == 'patient':
        search_db = db.query(Patient).filter(Patient.user_id == user_id).all()
        for current_user in search_db:
            if current_user.is_patient == True:
                current_user.is_patient = False
                current_user.status_expiry = datetime.now(timezone.utc)
                db.add(current_user)

    elif user.role == 'doctor':
        search_db = db.query(Doctor).filter(Doctor.user_id == user_id).all()
        for current_user in search_db:
            if current_user.is_doctor == True:
                current_user.is_doctor = False
                current_user.status_expiry = datetime.now(timezone.utc)
                db.add(current_user)
                
    elif user.role== 'admin':
        search_db = db.query(Admin).filter(Admin.user_id == user_id).all()
        for current_user in search_db:
            if current_user.is_admin == True:
                current_user.is_admin = False
                current_user.status_expiry = datetime.now(timezone.utc)
                db.add(current_user)
                
    # Set scheduled appointments to CANCELLED
    if user.role == 'patient' or user.role == 'doctor':
        appointments = get_user_appointments_by_user_id(user_id, db)
        for appointment in appointments:
            if appointment.status!= "CANCELLED":
                deactivate_appointment(appointment.appointment_id, db)
           
    # deactivate entry in User table
    user.is_valid = False
    db.commit()
    return {"message": "User Deactivated Successfully"}



@router.get("/getUserRole/")
def get_user_role(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:

        raise HTTPException(status_code=404, detail=user_not_found)
    else:

        return user.role
    
@router.get("/getUserInfo/")
def get_user_info( db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=user_not_found)
    else:
        info ={"user_id": user.user_id,
                "first_name":user.first_name,
                "last_name":user.last_name ,
                "username":user.username ,
                "email":user.email,
                "phone_number": user.phone_number,
                "role": user.role}
        if user.role == 'doctor':
            doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id, Doctor.is_doctor == 1).first()
            if doctor:
                info['doctor_id'] = doctor.doctor_id
                info['doctor_specialty'] = doctor.doctor_specialty
    return JSONResponse(content=info)



@router.put("/updateMyProfile/")
def update_my_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    # Ensure that the logged-in user is a doctor and they are updating their own information
    user = db.query(User).filter(User.user_id == current_user.user_id, 
                                    User.is_valid == 1).first()
    if not user:
        raise HTTPException(status_code=403, detail=general_privileges_update)
    
    if current_user.role == "doctor" and user_update.doctor_specialty:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id, 
                                    Doctor.is_doctor == 1).first()
        if not doctor:
            raise HTTPException(status_code=403, detail=general_privileges_update)
        if user_update.doctor_specialty.upper() not in allowed_specialties:
            raise HTTPException(status_code=404, detail=invalid_doctor_specialty)
        doctor.doctor_specialty = user_update.doctor_specialty
        db.commit()
        db.refresh(doctor)
    # Update user fields dynamically
        # get first name and last name
    if user_update.first_name and user_update.first_name.isalpha():
            current_user.first_name = user_update.first_name
    if user_update.last_name and user_update.last_name.isalpha():
            current_user.last_name = user_update.last_name
    if user_update.email and is_email_valid(user_update.email):
            current_user.email = user_update.email
    if user_update.phone_number and is_phone_number_valid(user_update.phone_number):
            current_user.phone_number = user_update.phone_number
    if user_update.username:
        current_user.username = user_update.username

    db.commit()
    db.refresh(current_user)  # Refresh the user object with updated values

    return {"message": "User updated successfully", "user": current_user}
