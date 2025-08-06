"""

# FastAPI ilovasi va asosiy endpointlar

"""
from warnings import deprecated

from fastapi import FastAPI, Depends, HTTPException, status, File, Form, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from redis import Redis
from sqlalchemy.orm import Session
from typing import List
import boto3
from fastapi.middleware.cors import CORSMiddleware

from datetime import timedelta
import os
from .models import schemas, crud, auth, pdf_processor , openai_service, assignments
from .database import SessionLocal , engine
from .redis_client import get_redis

app = FastAPI(title="Learning platform")

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

S3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

@app.get("/")
async  def root():
    return {"message":"Welcome to the Learning platform"}

# authentication
@app.post("/register", response_model=schemas.User)
async def register(user:schemas.UserCreate, db:Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login")
async def login(form_data:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WW-Authenticate":"Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = auth.create_access_token(
        data={"sub":user.email}, expires_delta=access_token_expires
    )
    return {"access_token":access_token, "token_type":"bearer"}

@app.post("/logout")
async def logout(token:str=Depends(oauth2_scheme), redis:Redis = Depends(get_redis)):
    await redis.setex(f"blacklist:{token}", 1800, "true")
    return {"message":"successfully logged out"}

# topic endpoints
@app.get("/topics", response_model=List[schemas.Topic])
async def get_topics(db:Session = Depends(get_db), redis: Redis = Depends(get_redis)):
    cache_key = "topics_list"
    cached_topics = await redis.get(cache_key)
    if cached_topics:
        return schemas.Topic.parse_raw(cached_topics)
    topics = crud.get_topics(db)
    await redis.setex(cache_key, 3600, schemas.Topic.dump_list(topics))
    return topics


@app.get("topics/{topic_id}", response_model=schemas.TopicDetail)
async def get_topic(topic_id:int, db:Session=Depends(get_db), redis:Redis = Depends(get_redis)):
    cache_key = f"topic:{topic_id}"
    cached_topic = await redis.get(cache_key)
    if cached_topic:
        return schemas.TopicDetail.parse_raw(cached_topic)
    topic = crud.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    await redis.setex(cache_key, 3600, schemas.TopicDetail.dump(topic))
    return topic

@app.post("/admin/topics", response_model=schemas.Topic)
async def update_topic(
        topic_id:int,
        topic:schemas.TopicCreate,
        db:Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),
):
    db_topic = crud.get_topic(db, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return crud.update_topic(db, topic_id, topic)

@app.delete("/admin/topics/{topic_id}")
async  def delete_topic(
        topic_id:int,
        db:Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),
):
    db_topic = crud.get_topic(db, topic_id)
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic nout found")
    crud.delete_topic(db, topic_id)
    return {"message":"Topic deleted successfully"}

@app.post("/admin/topics/{topic_id}/items")
async def create_topic_item(
    topic_id: int,
    item: schemas.TopicItemCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),
):
    item.topic_id = topic_id
    return crud.create_topic_item(db,item)












