from pydantic import BaseModel
from datetime import datetime, date

# pydantic model for appointment
class AppointmentCreate(BaseModel):
    patient_id : int
    doctor_id : int
    description : str
    date_time : datetime
    
class AdminAppointmentUpdate(BaseModel):
    description : str
    date_time : datetime
    status : str

class UserAppointmentUpdate(BaseModel):
    description : str
    date_time: datetime
    status: str

class getAvailableAppointment(BaseModel):
    doctor_id: int
    specialty: str
    date: date
    
class getdAvailableAppointmentByAppointmentId(BaseModel):
    appointment_id: int
    date: date
    
class patientAddAppointment(BaseModel):
    patient_id: int 
    date: date
    doctor_id: int
    time_slot: int
    description: str
