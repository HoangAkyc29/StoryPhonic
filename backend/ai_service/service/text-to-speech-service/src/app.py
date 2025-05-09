import os
import uuid
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
import threading
from collections import defaultdict

# Cấu hình
BASE_DIR = Path(__file__).parent.parent
app = FastAPI(title="TTS Service with Folder-based Task Control")

# Database tạm (production nên dùng Redis/Database)
TASK_DB: Dict[str, dict] = {}  # Lưu task theo task_id
FOLDER_TASK_MAP: Dict[str, str] = {}  # Ánh xạ folder_name -> task_id đang chạy
TASK_LOCK = threading.Lock()  # Lock để đồng bộ hoá truy cập vào FOLDER_TASK_MAP

class TaskRequest(BaseModel):
    narrative_annotation_dir: str
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

def get_folder_name(narrative_annotation_dir: str) -> str:
    """Trích xuất last folder name từ đường dẫn"""
    return os.path.basename(os.path.normpath(narrative_annotation_dir))

def run_tts_task(task_id: str, folder_name: str, request_data: dict):
    """Hàm xử lý dài hạn chạy trong background"""
    try:
        # Cập nhật trạng thái
        with TASK_LOCK:
            TASK_DB[task_id].status = "running"
            TASK_DB[task_id].start_time = datetime.now().isoformat()
        
        # Giả lập tiến trình (thay bằng code thực tế của bạn)
        from process_generate_emotion_audio import generate_all_TTS_with_emotion
        
        # Gọi hàm xử lý chính
        output_dir = generate_all_TTS_with_emotion(
            narrative_annotation_dir=request_data["narrative_annotation_dir"],
            emotion_audio_dir=request_data["emotion_audio_dir"],
            transcript_emotion_dir=request_data["transcript_emotion_dir"],
            output_dir=request_data["output_dir"]
        )
        
        # Cập nhật khi hoàn thành
        with TASK_LOCK:
            TASK_DB[task_id].status = "completed"
            TASK_DB[task_id].output_dir = output_dir
            TASK_DB[task_id].end_time = datetime.now().isoformat()
            TASK_DB[task_id].progress = 100.0
            # Giải phóng folder_name khi hoàn thành
            if FOLDER_TASK_MAP.get(folder_name) == task_id:
                del FOLDER_TASK_MAP[folder_name]
        
    except Exception as e:
        with TASK_LOCK:
            TASK_DB[task_id].status = "failed"
            TASK_DB[task_id].message = str(e)
            TASK_DB[task_id].end_time = datetime.now().isoformat()
            # Giải phóng folder_name khi lỗi
            if FOLDER_TASK_MAP.get(folder_name) == task_id:
                del FOLDER_TASK_MAP[folder_name]

@app.post("/generate-emotion-audio", response_model=TaskStatus)
async def create_tts_task(request: TaskRequest):
    """Khởi tạo task xử lý dài hạn"""
    folder_name = get_folder_name(request.narrative_annotation_dir)
    
    with TASK_LOCK:
        # Kiểm tra nếu folder đang được xử lý
        if folder_name in FOLDER_TASK_MAP:
            existing_task_id = FOLDER_TASK_MAP[folder_name]
            if existing_task_id in TASK_DB and TASK_DB[existing_task_id].status in ["pending", "running"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Folder '{folder_name}' is already being processed by task {existing_task_id}"
                )
        
        # Tạo task mới
        task_id = str(uuid.uuid4())
        TASK_DB[task_id] = TaskStatus(
            task_id=task_id,
            folder_name=folder_name,
            status="pending",
            start_time=datetime.now().isoformat()
        )
        FOLDER_TASK_MAP[folder_name] = task_id
    
    # Chạy task trong background thread
    thread = threading.Thread(
        target=run_tts_task,
        args=(task_id, folder_name, request.dict())
    )
    thread.start()
    
    return TASK_DB[task_id]

@app.get("/task-status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Kiểm tra trạng thái task"""
    if task_id not in TASK_DB:
        raise HTTPException(status_code=404, detail="Task not found")
    return TASK_DB[task_id]

@app.get("/folder-status/{folder_name}")
async def get_folder_status(folder_name: str):
    """Kiểm tra trạng thái theo folder name"""
    with TASK_LOCK:
        task_id = FOLDER_TASK_MAP.get(folder_name)
        if task_id and task_id in TASK_DB:
            return TASK_DB[task_id]
        return {"status": "available", "folder_name": folder_name}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=5001)