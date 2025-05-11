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

# Cấu hình
BASE_DIR = Path(__file__).parent.parent
DEFAULT_PATHS = {
    "audio_dir3": r"D:\FINAL_CODE\backend\ai_service\data\voice_data\temporary_output_voice_data\text_to_speech",
    "json_dir": r"D:\FINAL_CODE\backend\ai_service\data\voice_data\reference_voice_data\character_personality_mapping_by_lore",
    "audio_dir1": r"D:\FINAL_CODE\backend\ai_service\data\voice_data\reference_voice_data\character_voices",
    "output_dir": r"D:\FINAL_CODE\backend\ai_service\data\voice_data\temporary_output_voice_data\voice_conversion",
    "config_path":  r".\src\seed-vc\configs\presets\config_dit_mel_seed_uvit_whisper_base_f0_44k.yml",
    "checkpoint_path": r".\src\ai_model\DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema.pth"
}

app = FastAPI(title="Voice Conversion Service with Task Control")

# Database tạm (production nên dùng Redis/Database)
TASK_DB: Dict[str, dict] = {}  # Lưu task theo task_id
CONSTANT_ID_TASK_MAP: Dict[str, str] = {}  # Ánh xạ constant_id -> task_id đang chạy
TASK_LOCK = threading.Lock()  # Lock để đồng bộ hoá truy cập

class VoiceConversionRequest(BaseModel):
    audio_dir3: Optional[str] = None
    json_dir: Optional[str] = None
    audio_dir1: Optional[str] = None
    output_dir: Optional[str] = None
    config_path: Optional[str] = None
    checkpoint_path: Optional[str] = None
    narrator_gender: int = 0  # 0 là male, 1 là female
    constant_id: str  # Bắt buộc cung cấp constant_id

class TaskStatus(BaseModel):
    task_id: str
    constant_id: str
    status: str  # pending|running|completed|failed
    start_time: str
    end_time: Optional[str] = None
    output_dir: Optional[str] = None
    message: Optional[str] = None

def run_voice_conversion_task(task_id: str, constant_id: str, request_data: dict):
    """Hàm xử lý dài hạn chạy trong background"""
    try:
        # Cập nhật trạng thái
        with TASK_LOCK:
            TASK_DB[task_id].status = "running"
            TASK_DB[task_id].start_time = datetime.now().isoformat()
        
        # Gọi hàm xử lý chính
        from src.process_generate_voice_conversion_audio import generate_end_output_audio
        
        output_dir = generate_end_output_audio(
            audio_dir3=request_data["audio_dir3"],
            json_dir=request_data["json_dir"],
            audio_dir1=request_data["audio_dir1"],
            output_dir=request_data["output_dir"],
            config_path=request_data["config_path"],
            checkpoint_path=request_data["checkpoint_path"],
            narrator_gender=request_data["narrator_gender"],
            constant_id=constant_id
        )
        
        # Cập nhật khi hoàn thành
        with TASK_LOCK:
            TASK_DB[task_id].status = "completed"
            TASK_DB[task_id].output_dir = output_dir
            TASK_DB[task_id].end_time = datetime.now().isoformat()
            # Giải phóng constant_id khi hoàn thành
            if CONSTANT_ID_TASK_MAP.get(constant_id) == task_id:
                del CONSTANT_ID_TASK_MAP[constant_id]
        
    except Exception as e:
        with TASK_LOCK:
            TASK_DB[task_id].status = "failed"
            TASK_DB[task_id].message = str(e)
            TASK_DB[task_id].end_time = datetime.now().isoformat()
            # Giải phóng constant_id khi lỗi
            if CONSTANT_ID_TASK_MAP.get(constant_id) == task_id:
                del CONSTANT_ID_TASK_MAP[constant_id]

@app.post("/generate-voice-conversion", response_model=TaskStatus)
async def create_voice_conversion_task(request: VoiceConversionRequest):
    """Khởi tạo task voice conversion"""
    constant_id = request.constant_id
    
    with TASK_LOCK:
        # Kiểm tra nếu constant_id đang được xử lý
        if constant_id in CONSTANT_ID_TASK_MAP:
            existing_task_id = CONSTANT_ID_TASK_MAP[constant_id]
            if existing_task_id in TASK_DB and TASK_DB[existing_task_id].status in ["pending", "running"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Constant ID '{constant_id}' is already being processed by task {existing_task_id}"
                )
        
        # Tạo task mới
        task_id = str(uuid.uuid4())
        TASK_DB[task_id] = TaskStatus(
            task_id=task_id,
            constant_id=constant_id,
            status="pending",
            start_time=datetime.now().isoformat()
        )
        CONSTANT_ID_TASK_MAP[constant_id] = task_id
    
    # Xử lý các đường dẫn đầu ra
    audio_dir3 = request.audio_dir3 or DEFAULT_PATHS["audio_dir3"]
    json_dir = request.json_dir or DEFAULT_PATHS["json_dir"]
    audio_dir1 = request.audio_dir1 or DEFAULT_PATHS["audio_dir1"]
    output_dir = request.output_dir or DEFAULT_PATHS["output_dir"]
    config_path = request.config_path or DEFAULT_PATHS["config_path"]
    checkpoint_path = request.checkpoint_path or DEFAULT_PATHS["checkpoint_path"]
    
    # Chạy task trong background thread
    thread = threading.Thread(
        target=run_voice_conversion_task,
        args=(task_id, constant_id, {
            "audio_dir3": audio_dir3,
            "json_dir": json_dir,
            "audio_dir1": audio_dir1,
            "output_dir": output_dir,
            "config_path": config_path,
            "checkpoint_path": checkpoint_path,
            "narrator_gender": request.narrator_gender
        })
    )
    thread.start()
    
    return TASK_DB[task_id]

@app.get("/task-status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Kiểm tra trạng thái task"""
    if task_id not in TASK_DB:
        raise HTTPException(status_code=404, detail="Task not found")
    return TASK_DB[task_id]

@app.get("/constant-status/{constant_id}")
async def get_constant_status(constant_id: str):
    """Kiểm tra trạng thái theo constant_id"""
    with TASK_LOCK:
        task_id = CONSTANT_ID_TASK_MAP.get(constant_id)
        if task_id and task_id in TASK_DB:
            return TASK_DB[task_id]
        return {"status": "available", "constant_id": constant_id}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)