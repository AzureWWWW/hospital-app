from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.patient import AdminUpdatePatient
from database import get_db

from core.utils import is_name_valid, get_current_user, get_current_admin
from models.user import User
from models.patient import Patient
from core.messages import admin_privileges, patient_not_found, status_expiry_change,user_not_found, general_privileges_getInfo
router = APIRouter()


@router.put("/update_patient_status_expiry/")
def update_doctor_status_expiry(patient_id: int, patient_info: AdminUpdatePatient, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=patient_not_found)
    if patient.status_expiry:
        raise HTTPException(status_code=404, detail= status_expiry_change)
    
    if patient_info.status_expiry <=  datetime.now(timezone.utc):
        patient.is_patient = 0
    patient.status_expiry = patient_info.status_expiry
    db.commit()
    db.refresh(patient)
    
def is_patient_valid(user_id:int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id==user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=patient_not_found)
    if patient.is_patient == 0:
        return 0
    return patient.patient_id

    
def get_patient_name_by_id(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id==patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=patient_not_found)
    user = db.query(User).filter(User.user_id == patient.user_id).first() 
    if not user:
        raise HTTPException(status_code=404, detail=user_not_found)
    return  f"{user.first_name} {user.last_name}"



def get_patient_id_by_username(patient_username: str, db: Session = Depends(get_db)):
    # user needs to enter first and last name

    user = db.query(User).filter(User.username == patient_username).first() 
    if not user:
        raise HTTPException(status_code=404, detail=user_not_found)
    patient = db.query(Patient).filter(Patient.user_id== user.user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=patient_not_found)
    return patient.patient_id
 


def get_patient_id_by_user_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first() 
    if not user:
        raise HTTPException(status_code=404, detail=user_not_found)
    patient = db.query(Patient).filter(Patient.user_id== user.user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=patient_not_found)
    return patient.patient_id

@router.get("/getAllPatients/")
def get_all_patients(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        info = []
        patient_db = db.query(Patient).all()
        for patient in patient_db:
            patient_name = get_patient_name_by_id(patient.patient_id,db)
            user = db.query(User).filter(User.user_id == patient.user_id).first() 
            if not user:
                raise HTTPException(status_code=404, detail=user_not_found)
            app_data = {"patient_id": patient.patient_id,
                        "patient_name":patient_name,
                        "username":user.username,
                        "status_expiry": patient.status_expiry,
                        "email":user.email,
                        "phone_number": user.phone_number}
            info.append(app_data)
        return info
    elif current_user.role == "doctor":
        info = []
        patient_db = db.query(Patient).filter(Patient.is_patient==1).all()
        for patient in patient_db:
            patient_name = get_patient_name_by_id(patient.patient_id,db)
            user = db.query(User).filter(User.user_id == patient.user_id).first() 
            if not user:
                raise HTTPException(status_code=404, detail=user_not_found)
            app_data = {
                "patient_id": patient.patient_id,
                "patient_name":patient_name,
            }
            info.append(app_data)
        return info
    raise HTTPException(status_code=404, detail=general_privileges_getInfo)

def get_patient_id(user_id: int, db: Session = Depends(get_db) ):
    patient = db.query(Patient).filter(Patient.user_id == user_id, Patient.is_patient == 1).first()
    if not patient:
        raise HTTPException(status_code=404, detail=patient_not_found)
    return patient.patient_id


    