from django.conf import settings
import boto3
from pathlib import Path
import os
from .file_service import get_data_dir

def upload_audio_to_s3(novel_id: str, audio_dir: str = None) -> dict:
    """
    Upload all audio files from the specified directory to S3 using boto3
    Returns a dictionary mapping original filenames to their S3 URLs
    """
    # Xác định đường dẫn thư mục audio
    if audio_dir is not None:
        audio_path = Path(audio_dir)
    else:
        base_dir = Path(get_data_dir())
        audio_path = base_dir / "voice_data" / "temporary_output_voice_data" / "voice_conversion" / novel_id

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio directory not found: {audio_path}")

    # Khởi tạo client S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region = settings.AWS_S3_REGION_NAME

    uploaded_files = {}
    for audio_file in audio_path.glob('*'):
        if audio_file.is_file():
            s3_key = f"novels/{novel_id}/{audio_file.name}"
            # Upload file lên S3
            s3.upload_file(
                str(audio_file),
                bucket_name,
                s3_key
            )
            # Tạo URL public
            url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
            uploaded_files[audio_file.name] = url
    return uploaded_files 