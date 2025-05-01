from datetime import datetime
from pydantic import BaseModel
from schemas.user import UserCreate, UserUpdate

class PatientUser(UserCreate):
    user_id: int
    
class AdminUpdatePatient(BaseModel):
    status_expiry : datetime = None