from openai import AsyncOpenAI
import os
from . import schemas, crud
from sqlalchemy.orm import Session

async def generate_feedback(topic_id: int, correct_count: int, total_questions: int, incorrect_answers: list, db: Session):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    topic = crud.get_topic(db, topic_id)
    incorrect_details = [
        f"Question ID {answer.question_id}: Selected {answer.selected_answer}"
        for answer in incorrect_answers
    ]
    prompt = f"""
    The user took a test on the topic '{topic.title}'.
    They answered {correct_count} out of {total_questions} questions correctly (score: {(correct_count/total_questions)*100:.2f}%).
    Incorrect answers: {', '.join(incorrect_details)}.
    Provide feedback on their mistakes and suggest topics to review.
    """
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful tutor providing constructive feedback."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content