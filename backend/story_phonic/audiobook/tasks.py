import threading
import time
import requests
from audiobook.models.novel import Novel
from audiobook.services.audio_service import upload_audio_to_s3

def check_narrative_annotation_status(input_id: str, novel: Novel) -> bool:
    """Check status of narrative annotation task"""
    try:
        response = requests.get(f"http://localhost:5000/input-status/{input_id}")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "completed":
                return True
            elif data["status"] in ["pending", "running"]:
                return False
            else:
                # Update novel status to error
                novel.status = "error"
                novel.save()
                return True
    except Exception as e:
        novel.status = "error"
        novel.save()
        return True
    return False

def check_tts_status(folder_name: str, novel: Novel) -> bool:
    """Check status of TTS task"""
    try:
        response = requests.get(f"http://localhost:5001/folder-status/{folder_name}")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "completed":
                return True
            elif data["status"] in ["pending", "running"]:
                return False
            else:
                novel.status = "error"
                novel.save()
                return True
    except Exception as e:
        novel.status = "error"
        novel.save()
        return True
    return False

def check_voice_conversion_status(constant_id: str, novel: Novel) -> bool:
    """Check status of voice conversion task"""
    try:
        response = requests.get(f"http://localhost:5002/constant-status/{constant_id}")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "completed":
                return True
            elif data["status"] in ["pending", "running"]:
                return False
            else:
                novel.status = "error"
                novel.save()
                return True
    except Exception as e:
        novel.status = "error"
        novel.save()
        return True
    return False

def check_merge_audio_status(constant_id: str, novel: Novel) -> bool:
    """Check status of merge audio task"""
    try:
        response = requests.get(f"http://localhost:5002/merge-audio-status/{constant_id}")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "completed":
                return True
            elif data["status"] in ["pending", "running"]:
                return False
            else:
                novel.status = "error"
                novel.save()
                return True
    except Exception as e:
        novel.status = "error"
        novel.save()
        return True
    return False

def process_narrative_annotation(novel: Novel, file_path: str) -> bool:
    """Process narrative annotation task"""
    try:
        # Call narrative annotation service
        response = requests.post(
            "http://localhost:5000/generate-label-data",
            json={
                "input_id": str(novel.id),
                "input_data": file_path
            }
        )
        if response.status_code != 200:
            novel.status = "error_1"  # Error at step 1
            novel.save()
            return False

        # Wait for completion
        while not check_narrative_annotation_status(str(novel.id), novel):
            time.sleep(60)  # Check every minute

        return novel.status != "error_1"
    except Exception as e:
        novel.status = "error_1"  # Error at step 1
        novel.save()
        return False

def process_tts(novel: Novel) -> bool:
    """Process TTS task"""
    try:
        # Call TTS service
        response = requests.post(
            "http://localhost:5001/generate-emotion-audio",
            json={
                "annotation_id": str(novel.id)
            }
        )
        if response.status_code != 200:
            novel.status = "error_2"  # Error at step 2
            novel.save()
            return False

        # Wait for completion
        while not check_tts_status(str(novel.id), novel):
            time.sleep(60)  # Check every minute

        return novel.status != "error_2"
    except Exception as e:
        novel.status = "error_2"  # Error at step 2
        novel.save()
        return False

def process_voice_conversion(novel: Novel) -> bool:
    """Process voice conversion task"""
    try:
        # Call voice conversion service
        response = requests.post(
            "http://localhost:5002/generate-voice-conversion",
            json={
                "constant_id": str(novel.id)
            }
        )
        if response.status_code != 200:
            novel.status = "error_3"  # Error at step 3
            novel.save()
            return False

        # Wait for completion
        while not check_voice_conversion_status(str(novel.id), novel):
            time.sleep(60)  # Check every minute

        return novel.status != "error_3"
    except Exception as e:
        novel.status = "error_3"  # Error at step 3
        novel.save()
        return False

def process_merge_audio(novel: Novel) -> bool:
    """Process merge audio task"""
    try:
        # Call merge audio service
        response = requests.post(
            "http://localhost:5002/merge-audio",
            json={
                "constant_id": str(novel.id)
            }
        )
        if response.status_code != 200:
            novel.status = "error_4"  # Error at step 4
            novel.save()
            return False

        # Wait for completion
        while not check_merge_audio_status(str(novel.id), novel):
            time.sleep(60)  # Check every minute

        return novel.status != "error_4"
    except Exception as e:
        novel.status = "error_4"  # Error at step 4
        novel.save()
        return False

def thread_create_audiobook(novel: Novel, file_path: str = None):
    """Main thread function to create audiobook"""
    try:
        # Step 1: Process narrative annotation
        if not process_narrative_annotation(novel, file_path or novel.content):
            return

        # Step 2: Process TTS
        if not process_tts(novel):
            return

        # Step 3: Process voice conversion
        if not process_voice_conversion(novel):
            return

        # Step 4: Process merge audio
        if not process_merge_audio(novel):
            return

        # Step 5: Upload to S3
        try:
            uploaded_files = upload_audio_to_s3(str(novel.id))
            
            # Find metadata and audio file URLs
            metadata_url = None
            audio_url = None
            
            for filename, url in uploaded_files.items():
                if filename.endswith('.json'):
                    metadata_url = url
                elif filename.endswith('.wav'):
                    audio_url = url
                if metadata_url and audio_url:
                    break
            
            # Update novel with URLs
            novel.s3_audio_metadata_url = metadata_url
            novel.s3_audio_file_url = audio_url
            novel.save()
            
        except Exception as e:
            novel.status = "error_5"  # Error at step 5
            novel.save()
            return

        # If all steps completed successfully
        novel.status = "completed"
        novel.save()

    except Exception as e:
        novel.status = "error_unknown"  # Unknown error
        novel.save() 