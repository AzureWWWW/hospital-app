# includes pydantic models
from datetime import datetime
from pydantic import BaseModel
from schemas.user import UserCreate    

class AdminUser(UserCreate):
    is_admin: bool
    user_id: int

# pydantic model for updating role
class RoleUpdate(BaseModel):
    new_role: str
    
class DefaultAdminUpdateAdmin(BaseModel):
    status_expiry : datetime | None = None
