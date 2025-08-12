"""

# PDF fayllarni qayta ishlash logikasi
"""

from fastapi import UploadFile
import pdf2image
from PIL import Image
import io
import boto3
import os
from uuid import uuid4


async def process_pdf(file: UploadFile, topic_id: int, s3_client) -> list:
    pdf_data = await file.read()
    images = pdf2image.convert_from_bytes(pdf_data, dpi=100)
    image_urls = []
    bucket_name = os.getenv("S3_BUCKET_NAME", "your-bucket-name")

    for i, image in enumerate(images):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG", quality=85)
        img_byte_arr = img_byte_arr.getvalue()

        file_key = f"topics/{topic_id}/page_{i + 1}_{uuid4()}.png"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=img_byte_arr,
            ContentType="image/png",
        )
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
        image_urls.append(image_url)

    return image_urls