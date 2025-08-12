from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime
from .models import UserRole, TopicItemType

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.user
    group_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    group_id: Optional[int] = None

class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: int
    users: List[User] = []

    model_config = ConfigDict(from_attributes = True)

class TopicItemBase(BaseModel):
    topic_id: int
    type: TopicItemType
    content: str
    order: int

class TopicItemCreate(TopicItemBase):
    pass

class TopicItem(TopicItemBase):
    id: int

    model_config = ConfigDict(from_attributes = True)

class TopicBase(BaseModel):
    title: str
    description: str

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    id: int
    created_at: datetime
    items: List[TopicItem] = []

    model_config = ConfigDict(from_attributes = True)

class TopicDetail(Topic):
    pass

class QuestionBase(BaseModel):
    test_id: int
    question_text: str
    options: List[str]
    correct_answer: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int

    model_config = ConfigDict(from_attributes = True)

class TestBase(BaseModel):
    topic_id: int
    title: str

class TestCreate(TestBase):
    pass

class Test(TestBase):
    id: int
    questions: List[Question] = []

    model_config = ConfigDict(from_attributes = True)

class Answer(BaseModel):
    question_id: int
    selected_answer: str

class TestSubmission(BaseModel):
    topic_id: int
    answers: List[Answer]

class TestResult(BaseModel):
    correct_count: int
    total_questions: int
    score: float
    feedback: str
    can_proceed: bool

class UserResponseBase(BaseModel):
    user_id: int
    question_id: int
    selected_answer: str

class UserResponseCreate(UserResponseBase):
    pass

class UserResponse(UserResponseBase):
    id: int
    submitted_at: datetime

    model_config = ConfigDict(from_attributes = True)

class FeedbackBase(BaseModel):
    user_id: int
    test_id: int
    feedback_text: str

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class PracticalAssignmentBase(BaseModel):
    topic_id: int
    title: str
    description: str

class PracticalAssignmentCreate(PracticalAssignmentBase):
    pass

class PracticalAssignment(PracticalAssignmentBase):
    id: int

    model_config = ConfigDict(from_attributes = True)

class IndependentAssignmentBase(BaseModel):
    group_id: int
    title: str
    description: str

class IndependentAssignmentCreate(IndependentAssignmentBase):
    pass

class IndependentAssignment(IndependentAssignmentBase):
    id: int

    model_config = ConfigDict(from_attributes = True)

class IndependentSubmissionBase(BaseModel):
    user_id: int
    assignment_id: int
    file_url: str

class IndependentSubmissionCreate(IndependentSubmissionBase):
    pass

class IndependentSubmissionGrade(BaseModel):
    score: float
    feedback: Optional[str] = None

class IndependentSubmission(IndependentSubmissionBase):
    id: int
    score: Optional[float] = None
    feedback: Optional[str] = None
    submitted_at: datetime

    model_config = ConfigDict(from_attributes = True)