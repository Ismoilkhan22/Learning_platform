from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models
import boto3
import os
from uuid import uuid4
import io

async def upload_assignment_file(file: UploadFile, assignment_id: int, s3_client) -> str:
    file_data = await file.read()
    bucket_name = os.getenv("S3_BUCKET_NAME")
    file_key = f"assignments/{assignment_id}/{uuid4()}_{file.filename}"
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_key,
        Body=file_data,
        ContentType=file.content_type,
    )
    file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
    return file_url

def create_practical_assignment(db: Session, assignment: schemas.PracticalAssignmentCreate):
    db_assignment = models.PracticalAssignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def create_independent_assignment(db: Session, assignment: schemas.IndependentAssignmentCreate):
    db_assignment = models.IndependentAssignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def create_independent_submission(db: Session, submission: schemas.IndependentSubmissionCreate):
    db_submission = models.IndependentSubmission(**submission.model_dump())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def grade_independent_submission(db: Session, submission_id: int, grade: schemas.IndependentSubmissionGrade):
    db_submission = db.query(models.IndependentSubmission).filter(models.IndependentSubmission.id == submission_id).first()
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db_submission.score = grade.score
    db_submission.feedback = grade.feedback
    db.commit()
    db.refresh(db_submission)
    return db_submission