from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm


app=FastAPI()

SECRET_KEY = "super_secret_key_12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="login")
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict):
    to_encode= data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не удолось подтвердить учетные данные",
        headers= {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str=payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username:str
    model_config = {"from_attributes": True}
class TaskCreate(BaseModel):
    name:str

class TaskResponse(BaseModel):
    id:int
    name: str
    done:bool
    model_config={"from_attributes":True}

SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base=declarative_base()

class User(Base):
    __tablename__="users"
    id= Column(Integer, primary_key=True, index= True)
    username=Column(String, unique = True, index = True)
    hashed_password=Column(String)

class Task(Base):
    __tablename__="tasks"
    id= Column(Integer, primary_key=True, index= True)
    name=Column(String)
    done=Column(Boolean, default=False)
    user_id= Column(Integer, ForeignKey("users.id"))

Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code= 400, detail=" Такое имя польщователя уже существует")
    hashed_password = get_password_hash(user.password)
    new_user = User(username = user.username, hashed_password = hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(from_data: OAuth2PasswordRequestForm= Depends(), db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username == from_data.username).first()
    if not user or not verify_password(from_data.password, user.hashed_password):
        raise HTTPException(status_code= 401, detail="Неверный логен или пороль")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}




@app.get("/")
def read_index():
    return FileResponse("index.html")

@app.get("/tasks", response_model= list[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.user_id == current_user.id).all()

@app.post("/tasks", response_model=TaskResponse)
def app_task(task:TaskCreate, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    new_task= Task(name=task.name, done=False, user_id= current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.patch("/tasks/{task_id}")
def mark_task_done(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task.done = True
    db.commit()
    return{"message": "Задача выполнена. "}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db:Session= Depends(get_db), current_user: User = Depends(get_current_user)):
    task=db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task)
    db.commit()
    return {"message": "Задача удалена"}