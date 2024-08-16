from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# FastAPI instance
app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.finance_tracker
users_collection = db.users
transactions_collection = db.transactions

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT setup
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if user is None:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register/")
async def register(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    users_collection.insert_one({"username": username, "hashed_password": hashed_password})
    return {"msg": "User registered successfully"}

@app.post("/transactions/")
async def create_transaction(description: str, amount: float, user: dict = Depends(get_current_user)):
    transaction = {
        "username": user["username"],
        "description": description,
        "amount": amount,
        "date": datetime.utcnow()
    }
    transactions_collection.insert_one(transaction)
    return {"msg": "Transaction added successfully"}

@app.get("/transactions/")
async def get_transactions(user: dict = Depends(get_current_user)):
    transactions = list(transactions_collection.find({"username": user["username"]}))
    return {"transactions": transactions}
