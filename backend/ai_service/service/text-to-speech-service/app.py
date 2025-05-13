import os
import uuid
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
import threading
from dotenv import load_dotenv

# Load biến môi trường từ file .env ngoài cùng project
load_dotenv(dotenv_path=Path(__file__).resolve().parents[4] / '.env.root')

# Lấy đường dẫn tuyệt đối từ biến môi trường
data_dir_absolute = os.getenv('DATA_DIR_ABSOLUTE')
if not data_dir_absolute:
    raise ValueError("DATA_DIR_ABSOLUTE must be set in .env file")

# --- Cấu hình đường dẫn và logging ---
BASE_DIR = Path(__file__).parent.parent

# Suy ra các đường dẫn mặc định từ DATA_DIR_ABSOLUTE
DEFAULT_PATHS = {
    "narrative_annotation_dir": str(Path(data_dir_absolute) / "context_data/character_label_data"),
    "emotion_audio_dir": str(Path(data_dir_absolute) / "voice_data/reference_voice_data/emotion_voices"),
    "transcript_emotion_dir": str(Path(data_dir_absolute) / "voice_data/reference_voice_data/emotion_voices_transcript"),
    "output_dir": str(Path(data_dir_absolute) / "voice_data/temporary_output_voice_data/text_to_speech")
}

# Cấu hình Logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "tts_service_errors.log"

# Thiết lập logger riêng cho tác vụ TTS
task_logger = logging.getLogger("tts_task")
task_logger.setLevel(logging.ERROR)

file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - TaskID: %(task_id)s - Folder: %(folder_name)s - Message: %(message)s')
file_handler.setFormatter(formatter)

if not task_logger.handlers:
    task_logger.addHandler(file_handler)

# Import từ package src
from src.process_generate_emotion_audio import generate_all_TTS_with_emotion

app = FastAPI(title="TTS Service with Folder-based Task Control")

# Database tạm (production nên dùng Redis/Database)
TASK_DB: Dict[str, dict] = {}  # Lưu task theo task_id
FOLDER_TASK_MAP: Dict[str, str] = {}  # Ánh xạ folder_name -> task_id đang chạy
TASK_LOCK = threading.Lock()  # Lock để đồng bộ hoá truy cập vào FOLDER_TASK_MAP

class TaskRequest(BaseModel):
    annotation_id: str
    narrative_annotation_dir: Optional[str] = None
    emotion_audio_dir: Optional[str] = None
    transcript_emotion_dir: Optional[str] = None
    output_dir: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    folder_name: str
    status: str  # pending|running|completed|failed
    start_time: str
    end_time: Optional[str] = None
    output_dir: Optional[str] = None
    progress: Optional[float] = 0.0
    message: Optional[str] = None

def get_folder_name(annotation_id: str) -> str:
    """Trích xuất last folder name từ đường dẫn"""
    return annotation_id

def run_tts_task(task_id: str, folder_name: str, request_data: dict):
    """Hàm xử lý dài hạn chạy trong background"""
    try:
        with TASK_LOCK:
            TASK_DB[task_id]["status"] = "running"
            TASK_DB[task_id]["start_time"] = datetime.now().isoformat()

        # Đảm bảo các đường dẫn tồn tại
        for path_key, path_value in request_data.items():
            if path_value and not os.path.exists(path_value):
                raise ValueError(f"Directory does not exist: {path_value}")

        # Gọi hàm xử lý chính
        output_dir = generate_all_TTS_with_emotion(
            narrative_annotation_dir=request_data["narrative_annotation_dir"],
            emotion_audio_dir=request_data["emotion_audio_dir"] or DEFAULT_PATHS["emotion_audio_dir"],
            transcript_emotion_dir=request_data["transcript_emotion_dir"] or DEFAULT_PATHS["transcript_emotion_dir"],
            output_dir=request_data["output_dir"] or DEFAULT_PATHS["output_dir"]
        )

        with TASK_LOCK:
            TASK_DB[task_id]["status"] = "completed"
            TASK_DB[task_id]["output_dir"] = output_dir
            TASK_DB[task_id]["end_time"] = datetime.now().isoformat()
            TASK_DB[task_id]["progress"] = 100.0
            if FOLDER_TASK_MAP.get(folder_name) == task_id:
                del FOLDER_TASK_MAP[folder_name]

    except Exception as e:
        error_message = f"Error in TTS task: {str(e)}"
        task_logger.error(
            error_message,
            exc_info=True,
            extra={'task_id': task_id, 'folder_name': folder_name}
        )
        with TASK_LOCK:
            TASK_DB[task_id]["status"] = "failed"
            TASK_DB[task_id]["message"] = str(e)
            TASK_DB[task_id]["end_time"] = datetime.now().isoformat()
            if FOLDER_TASK_MAP.get(folder_name) == task_id:
                del FOLDER_TASK_MAP[folder_name]

@app.post("/generate-emotion-audio", response_model=TaskStatus)
async def create_tts_task(request: TaskRequest):
    """Khởi tạo task xử lý dài hạn"""
    folder_name = get_folder_name(request.annotation_id)

    with TASK_LOCK:
        if folder_name in FOLDER_TASK_MAP:
            existing_task_id = FOLDER_TASK_MAP[folder_name]
            existing_task_details = TASK_DB.get(existing_task_id)
            if existing_task_details and isinstance(existing_task_details, dict) and \
               existing_task_details.get("status") in ["pending", "running"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Folder '{folder_name}' is already being processed by task {existing_task_id}"
                )

        task_id = str(uuid.uuid4())
        task_info = TaskStatus(
            task_id=task_id,
            folder_name=folder_name,
            status="pending",
            start_time=datetime.now().isoformat()
        )
        TASK_DB[task_id] = task_info.model_dump() if hasattr(task_info, 'model_dump') else task_info.dict()
        FOLDER_TASK_MAP[folder_name] = task_id

    # Xử lý các đường dẫn đầu ra
    narrative_annotation_dir = str(Path(request.narrative_annotation_dir or DEFAULT_PATHS["narrative_annotation_dir"]) / request.annotation_id)
    emotion_audio_dir = request.emotion_audio_dir or DEFAULT_PATHS["emotion_audio_dir"]
    transcript_emotion_dir = request.transcript_emotion_dir or DEFAULT_PATHS["transcript_emotion_dir"]
    output_dir = request.output_dir or DEFAULT_PATHS["output_dir"]

    thread = threading.Thread(
        target=run_tts_task,
        args=(task_id, folder_name, {
            "narrative_annotation_dir": narrative_annotation_dir,
            "emotion_audio_dir": emotion_audio_dir,
            "transcript_emotion_dir": transcript_emotion_dir,
            "output_dir": output_dir
        })
    )
    thread.start()

    return TASK_DB[task_id]

@app.get("/task-status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Kiểm tra trạng thái task"""
    task_data = TASK_DB.get(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatus(**task_data)

@app.get("/folder-status/{folder_name}")
async def get_folder_status(folder_name: str):
    """Kiểm tra trạng thái theo folder name"""
    with TASK_LOCK:
        task_id = FOLDER_TASK_MAP.get(folder_name)
        if task_id:
            task_data = TASK_DB.get(task_id)
            if task_data:
                return TaskStatus(**task_data)
        return {"status": "available", "folder_name": folder_name, "message": "No active task for this folder."}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len([t for t in TASK_DB.values() if t.get("status") in ["pending", "running"]])
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)