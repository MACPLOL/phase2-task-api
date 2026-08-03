from pwdlib import PasswordHash
import os
from datetime import datetime, timedelta, timezone
import jwt

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
def hash_password(password: str) -> str:
    #Receive the raw password from the user
    #use the password_hash variable to create
    #a secure hash
    hashed_password = password_hash.hash(password)

    #return the hash
    return hashed_password

def verify_password(password: str, hashed_password: str) -> bool:
    #Receive the password
    #Receive the hashed_password
    #Ask password_hash using tool to compare
    #password to its hashed version
    result = password_hash.verify(password, hashed_password)
    if result is True:
        return True
    return False
        #Return true or false depending on comparison

def create_access_token(user_id: int) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expiration,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token

def decode_access_token(token: str) -> int:
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    user_id = payload["sub"]

    return int(user_id)