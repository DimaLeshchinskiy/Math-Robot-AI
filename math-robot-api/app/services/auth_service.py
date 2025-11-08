from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config import config

def basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    correct_username = config.BASIC_AUTH_USERNAME
    correct_password = config.BASIC_AUTH_PASSWORD
    
    if (credentials.username != correct_username or 
        credentials.password != correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username