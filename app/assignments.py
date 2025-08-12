from django.contrib.contenttypes.models import ContentType
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models
import boto3
import os
from uuid import uuid4
import io


def create_practical_assigment(db:Session, assigment:schemas.PracticalAssigmentCreate):
    db_assigment = models.PracticalAssignment(**assigment.dict())
    db.add(db_assigment)
    db.commit()
    db.refresh(db_assigment)
    return db_assigment

def create_independent_assignment(db:Session, assignment:schemas.IndependentAssigmentCreate):
    db_assignment = models.IndependentAssignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

async def upload_assignment_file(file:UploadFile, assignment_id:int, s3_client)->str:
    bucket_name = os.getenv("S3_BUCKET_NAME", "your-bucket-name")
    file_key = f"assignments/{assignment_id}/{uuid4()}_{file.filename}"
    file_data = await file.read()
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_key,
        Body=file_data,
        ContentType=file.content_type,
    )
    file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
    return file_url

def create_independent_submission(db:Session, submission:schemas.IndependentSubmissionCreate):
    db_submission = models.IndependentSubmission(**submission.dict())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def grade_independent_submission(db:Session, submission_id:int, grade:schemas.IndependentSubmissionGrade):
    db_submission = db.query(models.IndependentSubmission).filter(models.IndependentSubmission.id == submission_id).first()
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db_submission.score = grade.score
    db_submission.feedback = grade.feedback
    db.commit()
    db.refresh(db_submission)
    return db_submission









