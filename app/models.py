"""
# SQLAlchemy ma'lumotlar bazasi modellari
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, JSON, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    user = "user"
    teacher = "teacher"
    superadmin = "superadmin"

class TopicItemType(str, enum.Enum):
    text = "text"
    image = "image"
    pdf = "pdf"
    video = "video"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user)
    group_id = Column(Integer, ForeignKey("grou[.id"), nullable=True)
    create_at = Column(DateTime, default=datetime.utcnow)
    responses = relationship("UserResponse", back_populates="user")
    submissions = relationship("IndependentSubmission", back_populates="user")
    group = relationship("Group", back_populates="users")


class Group(Base):
    __tablename__ = "groups"
    id  = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    users = relationship("User", back_populates="group")
    assignments = relationship("IndependentAssignment", back_populates="group")


class Topic(Base):
    __tabename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("TopicItem", back_populates="topic", order_by="TopicItem.order")
    tests = relationship("Test", back_populates="topic")
    assignments = relationship("PracticalAssignment",back_populates="topic")


class TopicItem(Base):
    __tablename__ = "topic_item"
    id = Column(Integer, primary_key=True, idnex=True)
    topic_id = Column(Integer, ForeignKey("topic.id"))
    type = Column(Enum(TopicItemType))
    context = Column(String)   # text , image , url , pdf url, or youtube url
    order = Column(Integer)
    topic = relationship("Topic", back_populates="items")


class Test(Base):
    __tablename__  = "tests"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    title = Column(String)
    topic = relationship("Topic", back_populates="tests")
    questions = relationship("Question", back_populates="test")
    feedback = relationship("Feedback", back_populates="test")

class Question(Base):
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    question_text = Column(String)
    options = Column(JSON)
    correct_answer = Column(String)
    test = relationship("Test", back_populates="questions")
    responses = relationship("UserResponse", back_populates="questions")


class UserResponse(Base):
    __tablename__ = "user_responses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_answer = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))
    feedback_text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="feedback")
    test = relationship("Test", back_populates="feedback")

class PracticalAssignment(Base):
    __tablename__ = "practical_assignment"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    title = Column(String)
    topic = relationship("Topic", back_populates="assignments")

class IndependentAssignment(Base):
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("group.id"))
    title = Column(String)
    description =Column(String)
    group = relationship("Group", back_populates="Assignments")
    submissions = relationship("IndependentSubmission", back_populates="assignment")


class IndependentSubmission(Base):
    __tablename__ = "independent_submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    assignment_id = Column(Integer, ForeignKey("independent_assignments.id"))
    file_url = Column(String)
    score = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="submissions")
    assignment = relationship("IndependentAssignment", back_populates="submissions")