from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from core.security import hash_password



# Database setup
DATABASE_URL = "sqlite:///./hospital.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create admin-user when database is initialized
def create_admin_user():
    from models.user import User
    from models.admin import Admin

    db: Session = SessionLocal()

    admin_user = db.query(User).filter(User.username=='admin').first()

    if not admin_user:
        new_user = User(
            username = 'admin',
            hashed_password =  hash_password("admin"),
            phone_number = '+212000000000',
            email = 'admin@admin.com',
            role = 'admin',
            is_valid = True
        )
        db.add(new_user)
        db.flush()

        new_admin = Admin(
            user_id = new_user.user_id,
            is_admin = True
        )
        db.add(new_admin)
        db.commit()
    db.close()

# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)  # Create tables
    create_admin_user()  # Ensure admin user exists
    
