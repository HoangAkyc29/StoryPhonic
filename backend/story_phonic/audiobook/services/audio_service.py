import os
from pathlib import Path
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .file_service import get_data_dir

def upload_audio_to_s3(novel_id: str, audio_dir: str) -> dict:
    """
    Upload all audio files from the specified directory to S3
    Returns a dictionary mapping original filenames to their S3 URLs
    """
    # Get the absolute path to the audio directory
    base_dir = Path(get_data_dir())
    audio_path = base_dir / "voice_data/temporary_output_voice_data/voice_conversion" / novel_id
    
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio directory not found: {audio_path}")
    
    uploaded_files = {}
    
    # Upload each audio file in the directory
    for audio_file in audio_path.glob('*'):
        if audio_file.is_file():
            # Create S3 path: novel_id/filename
            s3_path = f"novels/{novel_id}/{audio_file.name}"
            
            # Read file content
            with open(audio_file, 'rb') as f:
                file_content = f.read()
            
            # Upload to S3
            default_storage.save(s3_path, ContentFile(file_content))
            
            # Get the URL of the uploaded file
            file_url = default_storage.url(s3_path)
            uploaded_files[audio_file.name] = file_url
    
    return uploaded_files 