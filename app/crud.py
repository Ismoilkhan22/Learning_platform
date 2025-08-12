"""

# Ma'lumotlar bazasi operatsiyalari (CRUD)
"""
from http.client import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.util import deprecated

from . import models, schemas
from passlib.context import CryptContext



pwd_context = CryptContext(schemas=["bcrypt"], deprecated="auto")


def get_user_by_email(db:Session, email:str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db:Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db:Session):
    return db.query(models.User).all()


def create_user(db:Session, user:schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role, group_id=user.group_id)
    db.add(db_user)
    db.refresh(db_user)
    return db_user

def update_user(db:Session, user_id:int, user: schemas.UserUpdate):
    db_user = get_user(db,user_id)
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_group(db:Session, group_id:int):
    return db.query(models.Group).filter(models.Group.id == group_id).first()

def create_group(db:Session, group:schemas.GroupCreate):
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def add_user_to_group(db:Session, group_id:int , user_id:int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    db_group = get_group(db, group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    db_user.group_id = group_id
    db.commit()
    db.refresh(db_user)
    return db_user



def get_topics(db:Session):
    return db.query(models.Topic).all()

def get_topic(db:Session, topic_id:int):
    return db.query(models.Topic).filter(models.TOPic.id == topic_id).first()


def create_topic(db:Session, topic:schemas.TopicCreate):
    db_topic = models.Topic(**topic.dict())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def update_topic(db:Session, topic_id:int , topic:schemas.TopicCreate):
    db_topic = get_topic(db, topic_id)
    update_data = topic.dict()
    for key , value in update_data.items():
        setattr(db_topic, key, value)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def delete_topic(db:Session, topic_id:int):
    db_topic = get_topic(db, topic_id)
    db.delete(db_topic)
    db.commit()


def create_topic_item(db:Session, item:schemas.TopicItemCreate):
    db_item = models.TopicItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_tests_by_topic(db:Session, topic_id:int):
    return db.query(models.Test).filter(models.Test.topic_id == topic_id).all()


def create_test(db:Session, test:schemas.TestCreate):
    db_test = models.Test(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def get_questions_by_test(db:Session, test_id:int):
    return db.query(models.Question).filter(models.Question.test_id == test_id).all()

def create_question(db:Session, question:schemas.QuestionCreate):
    db_question = models.Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def calculate_test_score(db:Session, test_id:int, submission:schemas.TestSubmission):
    correct_count = 0
    for answer in submission.answers:
        if is_answer_correct(db,answer):
            correct_count+=1
    return correct_count

def is_answer_correct(db:Session, answer:schemas.Answer):
    question = db.query(models.Question).filter(models.Question.id == answer.question_id).first()
    return question and question.correct_answer == answer.selected_answer


def create_feedback(db:Session, feedback:schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

