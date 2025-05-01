from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.endpoints.users import deactivate_expired_users
from database import init_db
from api.api_router import api_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware # to enable CORS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apscheduler.triggers.cron import CronTrigger


# periodic check for valid users
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        deactivate_expired_users,
        CronTrigger(hour = 0, minute = 0), #every day at Midnight
        id="deactivate_expired_users",
        replace_existing=True
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()
        
# Initialize FastAPI app and lifespan
app = FastAPI(lifespan=lifespan)


scheduler = AsyncIOScheduler()


# allow requests from the frontend
origins = [
    "http://localhost:4200",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,       # Allow cookies or credentials if needed
    allow_methods=["*"],          # Allow all HTTP requests
    allow_headers=["*"],          # Allow all headers
)
# initialize database
init_db()

# Include API routes
app.include_router(api_router)





# # run the server with https
if __name__ == "__main__":
    uvicorn.run(
    app,
    host="0.0.0.0",
    port = 8432,
    ssl_keyfile="./key.pem", 
    ssl_certfile="./cert.pem",
    lifespan="on",
)
    
