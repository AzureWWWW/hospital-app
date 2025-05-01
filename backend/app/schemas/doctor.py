from datetime import datetime

from pydantic import BaseModel
from schemas.user import UserCreate, UserUpdate

class DoctorUser(UserCreate):
    user_id: int
    doctor_specialty: str
    
# class DoctorUpdate(UserUpdate):
#     doctor_specialty: str
    
class AdminUpdateDoctor(BaseModel):
    status_expiry : datetime = None