"""
# Pydantic sxemalari (API so'rov/javob modellari)
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .models import UserRole, TopicItem, TopicItemType, Topic


class UserBase(BaseModel):
    email:EmailStr
    role : UserRole = UserRole.student


class UserCreate(UserBase):
    password:str

class UserUpdate(UserBase):
    pass


class User(UserBase):
    id:int
    created_at:str

    class Config:
        orm_mode = True


class TopicItemBase(BaseModel):
    topic_id:int
    type: TopicItemType
    content:str
    order:int

class TopicItemCreate(TopicItemBase):
    pass

class TopicItem(TopicItemBase):
    id:int

    class Config:
        orm_mode = True

class TopicBase(BaseModel):
    title:str
    description:str

class TopicCreate(TopicBase):
    id:int
    created_at: datetime
    items: List[TopicItem] = []


    class Config:
        orm_mode = True


class TopicDetail(Topic):
    pass

class QuestionBase(BaseModel):
    test_id:int
    question_text:str
    options:List[str]
    correct_answer:str

class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id:int

    class Config:
        orm_mode = True


class TestBase(BaseModel):
    topic_id:int
    title:str


class TestCreate(TestBase):
    pass

class Test(TestBase):
    id:int
    questions: List[Question] = []

    class Config:
        orm_mode = True



class Answer(BaseModel):
    question_id:int
    selected_answer: str


class TestSubmission(BaseModel):
    topic_id:int
    answers: List[Answer]

class TestResult(BaseModel):
    correct_count:int
    total_question: int
    feedback: str


class UserResponseBase(BaseModel):
    user_id:int
    question_id: int
    selected_answer: str


class UserResponse(UserResponseBase):
    id:int
    submitted_at:datetime

    class Config:
        orm_mode = True

class FeedbackBase(BaseModel):
    user_id:int
    test_it:int
    feedback_text:str


class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id:int
    created_at:datetime

    class Config:
        orm_mode = True



