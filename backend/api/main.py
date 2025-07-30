from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import json
import time
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI(
    title="MedSecure API",
    description="Secure medical data management API with ML-based anomaly detection and blockchain integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock database (replace with actual database in production)
users_db = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "full_name": "Admin User",
        "role": "admin",
        "disabled": False
    },
    "doctor@example.com": {
        "email": "doctor@example.com",
        "hashed_password": pwd_context.hash("doctor123"),
        "full_name": "Dr. John Smith",
        "role": "doctor",
        "disabled": False
    },
    "nurse@example.com": {
        "email": "nurse@example.com",
        "hashed_password": pwd_context.hash("nurse123"),
        "full_name": "Nurse Sarah Johnson",
        "role": "nurse",
        "disabled": False
    },
    "patient@example.com": {
        "email": "patient@example.com",
        "hashed_password": pwd_context.hash("patient123"),
        "full_name": "Patient User",
        "role": "patient",
        "disabled": False
    }
}

# Mock patient records database
patient_records = []

# Mock access logs
access_logs = []

# Mock anomaly alerts
anomaly_alerts = []

# Models
class User(BaseModel):
    email: str
    full_name: str
    role: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str
    otp: str  # In a real app, implement actual OTP verification
    device_info: Dict[str, Any]  # Device posture information

class PatientRecord(BaseModel):
    id: Optional[str] = None
    patient_email: str
    record_type: str
    provider: str
    date: str
    description: str
    file_path: str
    file_hash: str
    ipfs_cid: Optional[str] = None
    blockchain_tx: Optional[str] = None
    created_at: Optional[str] = None
    
class AccessLog(BaseModel):
    timestamp: str
    user_email: str
    user_role: str
    action: str
    resource: str
    ip_address: str
    device_info: Dict[str, Any]
    trust_score: float
    
class AnomalyAlert(BaseModel):
    timestamp: str
    user_email: str
    user_role: str
    alert_type: str
    severity: str
    description: str
    raw_data: Dict[str, Any]
    
class ConsentRequest(BaseModel):
    patient_email: str
    provider_email: str
    access_level: str
    start_date: str
    end_date: str
    purpose: str
    
class TrustScoreRequest(BaseModel):
    user_email: str
    ip_address: str
    device_info: Dict[str, Any]
    access_time: str
    resource_type: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserInDB(**user_dict)
    return None

def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(users_db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Middleware for logging and anomaly detection
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Get client IP
    ip = request.client.host
    
    # Get path
    path = request.url.path
    
    # Get user from token if available
    user_email = "anonymous"
    user_role = "anonymous"
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email = payload.get("sub")
            user_role = payload.get("role")
        except:
            pass
    
    # Record start time
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Record end time
    process_time = time.time() - start_time
    
    # Log the request (in a real app, save to database)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_email": user_email,
        "user_role": user_role,
        "method": request.method,
        "path": path,
        "ip_address": ip,
        "process_time": process_time,
        "status_code": response.status_code
    }
    
    # In a real app, this would be sent to the ML model for anomaly detection
    # and the trust score would be calculated
    
    # For demo purposes, randomly flag some requests as anomalies
    if path not in ["/docs", "/openapi.json"] and time.time() % 20 < 1:
        anomaly_alerts.append({
            "timestamp": datetime.now().isoformat(),
            "user_email": user_email,
            "user_role": user_role,
            "alert_type": "Unusual Access Pattern",
            "severity": "medium",
            "description": f"Unusual access pattern detected for {user_email}",
            "raw_data": log_entry
        })
    
    return response

# Routes
@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    if user.role not in ["admin", "doctor", "nurse", "patient"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    users_db[user.email] = {
        "email": user.email,
        "hashed_password": hashed_password,
        "full_name": user.full_name,
        "role": user.role,
        "disabled": False
    }
    
    return {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "disabled": False
    }

@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = authenticate_user(users_db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real app, verify OTP here
    if login_data.otp != "123456":  # Dummy OTP check
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real app, check device posture here
    # For demo, we'll just log it
    device_info = login_data.device_info
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Log the login
    access_logs.append({
        "timestamp": datetime.now().isoformat(),
        "user_email": user.email,
        "user_role": user.role,
        "action": "login",
        "resource": "system",
        "ip_address": "127.0.0.1",  # In a real app, get from request
        "device_info": device_info,
        "trust_score": 0.85  # In a real app, calculate with ML model
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name
    }

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/upload", response_model=PatientRecord)
async def upload_record(
    record: PatientRecord,
    current_user: User = Depends(get_current_active_user)
):
    # Check permissions
    if current_user.role not in ["admin", "doctor", "patient"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload records"
        )
    
    # If user is a patient, they can only upload their own records
    if current_user.role == "patient" and record.patient_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients can only upload their own records"
        )
    
    # Generate record ID
    import uuid
    record_id = str(uuid.uuid4())
    
    # In a real app, handle file upload, encryption, and IPFS storage here
    # For demo, we'll just simulate it
    record.id = record_id
    record.created_at = datetime.now().isoformat()
    record.ipfs_cid = f"Qm{record_id[:46]}"  # Fake IPFS CID
    record.blockchain_tx = f"0x{record_id.replace('-', '')}"  # Fake blockchain transaction
    
    # Add to records
    patient_records.append(record.dict())
    
    # Log the upload
    access_logs.append({
        "timestamp": datetime.now().isoformat(),
        "user_email": current_user.email,
        "user_role": current_user.role,
        "action": "upload",
        "resource": f"record/{record_id}",
        "ip_address": "127.0.0.1",  # In a real app, get from request
        "device_info": {},  # In a real app, get from request
        "trust_score": 0.9  # In a real app, calculate with ML model
    })
    
    return record

@app.get("/records", response_model=List[PatientRecord])
async def get_records(current_user: User = Depends(get_current_active_user)):
    # Filter records based on user role
    if current_user.role == "admin":
        # Admins can see all records
        return patient_records
    elif current_user.role == "doctor":
        # Doctors can see records they uploaded or have consent for
        # In a real app, check consent on blockchain
        return patient_records
    elif current_user.role == "nurse":
        # Nurses can see records they have consent for (read-only)
        # In a real app, check consent on blockchain
        return patient_records
    elif current_user.role == "patient":
        # Patients can only see their own records
        return [r for r in patient_records if r["patient_email"] == current_user.email]
    else:
        return []

@app.get("/records/{record_id}", response_model=PatientRecord)
async def get_record(
    record_id: str,
    current_user: User = Depends(get_current_active_user)
):
    # Find the record
    record = next((r for r in patient_records if r["id"] == record_id), None)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )
    
    # Check permissions
    if current_user.role == "patient" and record["patient_email"] != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this record"
        )
    
    # In a real app, check consent on blockchain for doctors and nurses
    
    # Log the access
    access_logs.append({
        "timestamp": datetime.now().isoformat(),
        "user_email": current_user.email,
        "user_role": current_user.role,
        "action": "view",
        "resource": f"record/{record_id}",
        "ip_address": "127.0.0.1",  # In a real app, get from request
        "device_info": {},  # In a real app, get from request
        "trust_score": 0.85  # In a real app, calculate with ML model
    })
    
    return record

@app.get("/logs", response_model=List[Dict[str, Any]])
async def get_logs(current_user: User = Depends(get_current_active_user)):
    # Only admins can see all logs
    if current_user.role == "admin":
        return access_logs
    
    # Other users can only see their own logs
    return [log for log in access_logs if log["user_email"] == current_user.email]

@app.get("/alerts", response_model=List[Dict[str, Any]])
async def get_alerts(current_user: User = Depends(get_current_active_user)):
    # Only admins can see alerts
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view alerts"
        )
    
    return anomaly_alerts

@app.post("/predict/trust", response_model=Dict[str, Any])
async def predict_trust_score(
    request: TrustScoreRequest,
    current_user: User = Depends(get_current_active_user)
):
    # In a real app, this would call the ML model
    # For demo, we'll return a mock score
    
    # Only admins can check trust scores for other users
    if current_user.role != "admin" and request.user_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check trust score for other users"
        )
    
    # Mock trust score calculation
    import random
    base_score = 0.75
    
    # Add some randomness
    variation = random.uniform(-0.1, 0.1)
    
    # Adjust based on resource type
    if request.resource_type == "sensitive":
        base_score -= 0.05
    
    final_score = min(max(base_score + variation, 0), 1)
    
    return {
        "user_email": request.user_email,
        "timestamp": datetime.now().isoformat(),
        "trust_score": final_score,
        "factors": {
            "ip_reputation": random.uniform(0.7, 0.9),
            "device_posture": random.uniform(0.6, 0.95),
            "behavioral": random.uniform(0.7, 0.9),
            "historical": random.uniform(0.8, 0.95)
        },
        "threshold": 0.6,
        "access_granted": final_score >= 0.6
    }

@app.post("/predict/anomaly", response_model=Dict[str, Any])
async def predict_anomaly(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    # In a real app, this would call the Autoencoder model
    # For demo, we'll return a mock result
    
    # Only admins can run anomaly detection
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can run anomaly detection"
        )
    
    # Mock anomaly detection
    import random
    
    reconstruction_error = random.uniform(0, 0.2)
    threshold = 0.1
    is_anomaly = reconstruction_error > threshold
    
    if is_anomaly:
        # Add to alerts
        anomaly_alerts.append({
            "timestamp": datetime.now().isoformat(),
            "user_email": request.get("user_email", "unknown"),
            "user_role": request.get("user_role", "unknown"),
            "alert_type": "Anomaly Detection",
            "severity": "high" if reconstruction_error > 0.15 else "medium",
            "description": f"Unusual activity detected with reconstruction error {reconstruction_error:.4f}",
            "raw_data": request
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "reconstruction_error": reconstruction_error,
        "threshold": threshold,
        "is_anomaly": is_anomaly,
        "severity": "high" if reconstruction_error > 0.15 else "medium" if is_anomaly else "low"
    }

@app.post("/contracts/consent", response_model=Dict[str, Any])
async def manage_consent(
    consent: ConsentRequest,
    current_user: User = Depends(get_current_active_user)
):
    # In a real app, this would interact with the blockchain
    # For demo, we'll just return a mock result
    
    # Patients can only manage their own consent
    if current_user.role == "patient" and consent.patient_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients can only manage their own consent"
        )
    
    # Generate a fake transaction hash
    import uuid
    tx_hash = f"0x{uuid.uuid4().hex}"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "patient_email": consent.patient_email,
        "provider_email": consent.provider_email,
        "access_level": consent.access_level,
        "start_date": consent.start_date,
        "end_date": consent.end_date,
        "purpose": consent.purpose,
        "blockchain_tx": tx_hash,
        "status": "confirmed"
    }

@app.get("/contracts/logs", response_model=List[Dict[str, Any]])
async def get_blockchain_logs(current_user: User = Depends(get_current_active_user)):
    # In a real app, this would fetch logs from the blockchain
    # For demo, we'll return mock data
    
    # Generate some fake blockchain logs
    logs = []
    for i in range(10):
        logs.append({
            "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            "block_number": 1000000 + i,
            "transaction_hash": f"0x{i:064x}",
            "event_type": "ConsentGranted" if i % 3 == 0 else "AccessLog" if i % 3 == 1 else "DataHashStored",
            "user": current_user.email if i % 2 == 0 else "other@example.com",
            "data": {
                "resource_id": f"resource_{i}",
                "access_level": "read" if i % 2 == 0 else "write"
            }
        })
    
    return logs

@app.post("/nlp/scan", response_model=Dict[str, Any])
async def scan_text(
    request: Dict[str, str],
    current_user: User = Depends(get_current_active_user)
):
    # In a real app, this would call the BERT model
    # For demo, we'll return a mock result
    
    if "text" not in request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text field is required"
        )
    
    text = request["text"]
    
    # Mock PHI detection
    import re
    
    # Simple patterns for demonstration
    patterns = {
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "address": r"\b\d+\s+[A-Za-z]+\s+[A-Za-z]+\b"
    }
    
    findings = {}
    for category, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            findings[category] = matches
    
    has_phi = len(findings) > 0
    
    # If PHI is detected, log an alert for admins
    if has_phi:
        anomaly_alerts.append({
            "timestamp": datetime.now().isoformat(),
            "user_email": current_user.email,
            "user_role": current_user.role,
            "alert_type": "PHI Detection",
            "severity": "high",
            "description": f"Potential PHI detected in text submitted by {current_user.email}",
            "raw_data": {
                "categories": list(findings.keys()),
                "user": current_user.email
            }
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "has_phi": has_phi,
        "categories": list(findings.keys()),
        "confidence": 0.92 if has_phi else 0.05,
        "recommendation": "Review and remove PHI" if has_phi else "No PHI detected"
    }

@app.post("/ipfs/upload", response_model=Dict[str, str])
async def upload_to_ipfs(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    # In a real app, this would upload to IPFS
    # For demo, we'll return a mock CID
    
    if "data" not in request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data field is required"
        )
    
    # Generate a fake IPFS CID
    import uuid
    cid = f"Qm{uuid.uuid4().hex[:46]}"
    
    return {
        "cid": cid,
        "timestamp": datetime.now().isoformat(),
        "size": len(str(request["data"]))
    }

@app.get("/ipfs/fetch/{cid}", response_model=Dict[str, Any])
async def fetch_from_ipfs(
    cid: str,
    current_user: User = Depends(get_current_active_user)
):
    # In a real app, this would fetch from IPFS
    # For demo, we'll return mock data
    
    # Check if CID is valid format
    if not cid.startswith("Qm"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid IPFS CID format"
        )
    
    # Mock data
    return {
        "cid": cid,
        "data": {"mock": "This is encrypted data that would be fetched from IPFS"},
        "timestamp": datetime.now().isoformat()
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)