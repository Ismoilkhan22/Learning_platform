"""

# FastAPI ilovasi va asosiy endpointlar

"""
from ctypes.wintypes import HHOOK
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
from . import models, schemas, crud, auth, pdf_processor , openai_service, assignments
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


@app.post("/admin/uploud_pdf")
async def upload_pdf(
        file:UploadFile = File(...),
        topic_id: int = Form(...),
        order: int = Form(...),
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(auht.get_current_teacher_or_admin),
):
    try:
        image_url = await pdf_processor.process_pdf(file,topic_id,s3_client)
        for i, url in enumerate(image_url, start=order):
            crud.create_topic_item(
                db,
                schemas.TopicItemCreate(
                    topic_id=topic_id,
                    type="image",
                    content=url,
                    order=i,
                ),
            )
        return {"message:PDF processed and images upload successfully "}
    except Exception as e:
        return HTTPException(status_code=500, detail=f"pdf processing failed: {str(e)}")

# test endpoints

@app.get("/topics/{topic_id}/tests", response_model=List[schemas.Test])
async  def get_tests(topic_id:int, db:Session = Depends(get_db)):
    tests = crud.get_tests_by_topic(db, topic_id)
    return tests

@app.get("/tests/{test_id}/questions", response_model=List[schemas.Question])
async def get_questions(test_id:int, db:Session = Depends(get_db), redis: Redis = Depends(get_redis)):
    cache_key = f"questions:{test_id}"
    cached_question = await redis.get(cache_key)
    if cached_question:
        return schemas.Question.parse_raw(cached_question)
    questions = crud.get_question_by_test(db, test_id)
    await redis.setex(cache_key, 3600, schemas.Question.dump_list(questions))
    return questions

@app.post("/tests/{test_id/submit}", response_model=schemas.TestResult)
async def submit_test(
        test_id:int,
        submission:schemas.TestSubmission,
        db:Session = Depends(get_db),
        current_user:schemas.User = Depends(auth.get_current_user),

):
    correct_count = crud.calculate_test_score(db, test_id, submission)
    total_questions = len(crud.get_question_by_test(db, test_id))
    score = (correct_count / total_questions)*100
    feedback = ""
    if score <60:
        feedback = await openai_service.generate_feedback(
            topic_id = submission.topic_id,
            correct_count=correct_count,
            total_questions=total_questions,
            incorrect_answer=[
                answer for answer in submission.answer if not crud.is_answer_correct(db,answer)
            ],
            db=db,
        )
        return schemas.TestResult(
            correct_count=correct_count,
            total_questions=total_questions,
            score=score,
            feedback=feedback,
            can_proceed=False,
        )
    crud.create_feedback(
        db,
        schemas.FeedbackCreate(
            user_id=current_user.id,
            test_id=test_id,
            feedback_text = feedback or "Good job!",
        ),
    )
    return schemas.TestResult(
        correct_count=correct_count,
        total_questions=total_questions,
        score=score,
        feedback=feedback or "Good job",
        can_proceed = True,
    )
@app.post("/admin/tests", response_model=schemas.Test)
async def create_test(
        test:schemas.TestCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),
):
    return crud.create_user_test(db,test)

@app.post("/admin/question", response_model=schemas.Question)
async def create_question(
        question: schemas.QuestionCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),
):
    return crud.create_user_question(db,question)


# Assignment endpoints

@app.post("/assignments/practical", response_model=schemas.PracticalAssignment)
async def create_practical_assignment(
        assignment: schemas.PracticalAssignmentCreate,
        db:Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),
):
    return assignments.create_practical_assignment(db,assignment)

@app.post("/assignments/independent", response_model=schemas.IndependentAssignment)
async def create_independent_assignment(
        assignment:schemas.IndependentAssignmentCreate,
        db:Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),
):
    return assignments.create_independent_assignment(db, assignment)

@app.post("/assignments/independent/{assignment_id}/submit")
async def submit_independent_assignment(
        assignment_id:int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_user),
):
    file_url = await assignments.upload_assignment_file(file, assignment_id, s3_client)
    return assignments.create_independent_submission(
        db, schemas.IndependentSubmissionCreate(
            user_id=current_user.id,
            assignment_id=assignment_id,
            file_url=file_url,
        )
    )

@app.post("/assignments/independent/{submission_id}/grade")
async def grade_independent_assignment(
        submission_id:int,
        grade: schemas.IndependentSubmissionGrade,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_teacher_or_admin),

):
    return assignments.grade_independent_submission(db, submission_id, grade)

# Group Endpoints

@app.post("/admin/groups", response_model=schemas.Grou)
async def create_group(
        group:schemas.GroupCreate,
        db:Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_admin),
):
    return crud.create_group(db, group)

@app.post("/admin/groups/{group_id}/users")
async def  add_user_to_group(
        group_id:int,
        user_id:int,
        db:Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_admin),
):
    return crud.add_user_to_group(db,group_id, user_id)


# Superadmin Endpoints


@app.put("/admin/users/{user_id}", response_model=schemas.User)
async def update_user(
        user_id:int,
        user:schemas.UserUpdate,
        db:Session = Depends(get_db),
        current_user:schemas.User = Depends(auth.get_current_admin)
):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db, user_id, user)













