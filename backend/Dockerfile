FROM python:3.13.2-slim
WORKDIR /HospitalApp/backend

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .
WORKDIR /HospitalApp/backend/app/


# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8432"]