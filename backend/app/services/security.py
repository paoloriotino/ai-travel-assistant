from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Configurazione JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "un_segreto_super_sicuro_per_sviluppo_123!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 giorni

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica che la password in chiaro corrisponda all'hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Genera l'hash bcrypt per una password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT firmato."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
