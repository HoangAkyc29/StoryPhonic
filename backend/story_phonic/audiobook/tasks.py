import threading
import time
import requests
from ..models.novel import Novel

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
            novel.status = "error"
            novel.save()
            return False

        # Wait for completion
        while not check_narrative_annotation_status(str(novel.id), novel):
            time.sleep(60)  # Check every minute

        return novel.status != "error"
    except Exception as e:
        novel.status = "error"
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
            novel.status = "error"
            novel.save()
            return False

        # Wait for completion
        while not check_tts_status(str(novel.id), novel):
            time.sleep(60)  # Check every minute

        return novel.status != "error"
    except Exception as e:
        novel.status = "error"
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
            novel.status = "error"
            novel.save()
            return False

        # Wait for completion
        while not check_voice_conversion_status(str(novel.id), novel):
            time.sleep(60)  # Check every minute

        return novel.status != "error"
    except Exception as e:
        novel.status = "error"
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

        # If all steps completed successfully
        novel.status = "completed"
        novel.save()

    except Exception as e:
        novel.status = "error"
        novel.save() 