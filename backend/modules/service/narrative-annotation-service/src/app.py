import os
import uuid
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
import threading
from collections import defaultdict

# Cấu hình
BASE_DIR = Path(__file__).parent.parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "context_data"
app = FastAPI(title="Narrative Annotation Service with Task Control")

# Database tạm (production nên dùng Redis/Database)
TASK_DB: Dict[str, dict] = {}  # Lưu task theo task_id
INPUT_ID_TASK_MAP: Dict[str, str] = {}  # Ánh xạ input_id -> task_id đang chạy
TASK_LOCK = threading.Lock()  # Lock để đồng bộ hoá truy cập

class TaskRequest(BaseModel):
    input_data: str
    input_id: str  # Bắt buộc phải cung cấp input_id
    output_dir: Optional[str] = None
    memory_dir: Optional[str] = None
    character_personality_output_dir: Optional[str] = None
    validate_identity_character_personality_output_dir: Optional[str] = None
    final_identity_character_dir: Optional[str] = None
    voice_personality_dir: Optional[str] = None
    voice_personality_by_lore_dir: Optional[str] = None
    character_voice_mapper_dir: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    input_id: str
    status: str  # pending|running|completed|failed
    start_time: str
    end_time: Optional[str] = None
    result_dirs: Optional[dict] = None
    message: Optional[str] = None

def run_label_data_task(task_id: str, input_id: str, request_data: dict):
    """Hàm xử lý dài hạn chạy trong background"""
    try:
        # Cập nhật trạng thái
        with TASK_LOCK:
            TASK_DB[task_id].status = "running"
            TASK_DB[task_id].start_time = datetime.now().isoformat()
        
        # Gọi hàm xử lý chính
        from generate_label_data import generate_label_data_main
        
        result_dirs = generate_label_data_main(
            input_data=request_data["input_data"],
            input_id=input_id,
            output_dir=request_data["output_dir"],
            memory_dir=request_data["memory_dir"],
            character_personality_output_dir=request_data["character_personality_output_dir"],
            validate_identity_character_personality_output_dir=request_data["validate_identity_character_personality_output_dir"],
            final_identity_character_dir=request_data["final_identity_character_dir"],
            voice_personality_dir=request_data["voice_personality_dir"],
            voice_personality_by_lore_dir=request_data["voice_personality_by_lore_dir"],
            character_voice_mapper_dir=request_data["character_voice_mapper_dir"]
        )
        
        # Cập nhật khi hoàn thành
        with TASK_LOCK:
            TASK_DB[task_id].status = "completed"
            TASK_DB[task_id].result_dirs = {
                "label_data_dir": result_dirs[0],
                "personality_data_dir": result_dirs[1],
                "final_identity_dir": result_dirs[2]
            }
            TASK_DB[task_id].end_time = datetime.now().isoformat()
            # Giải phóng input_id khi hoàn thành
            if INPUT_ID_TASK_MAP.get(input_id) == task_id:
                del INPUT_ID_TASK_MAP[input_id]
        
    except Exception as e:
        with TASK_LOCK:
            TASK_DB[task_id].status = "failed"
            TASK_DB[task_id].message = str(e)
            TASK_DB[task_id].end_time = datetime.now().isoformat()
            # Giải phóng input_id khi lỗi
            if INPUT_ID_TASK_MAP.get(input_id) == task_id:
                del INPUT_ID_TASK_MAP[input_id]

@app.post("/generate-label-data", response_model=TaskStatus)
async def create_label_data_task(request: TaskRequest):
    """Khởi tạo task xử lý dài hạn"""
    input_id = request.input_id
    
    with TASK_LOCK:
        # Kiểm tra nếu input_id đang được xử lý
        if input_id in INPUT_ID_TASK_MAP:
            existing_task_id = INPUT_ID_TASK_MAP[input_id]
            if existing_task_id in TASK_DB and TASK_DB[existing_task_id].status in ["pending", "running"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Input ID '{input_id}' is already being processed by task {existing_task_id}"
                )
        
        # Tạo task mới
        task_id = str(uuid.uuid4())
        TASK_DB[task_id] = TaskStatus(
            task_id=task_id,
            input_id=input_id,
            status="pending",
            start_time=datetime.now().isoformat()
        )
        INPUT_ID_TASK_MAP[input_id] = task_id
    
    # Xử lý các đường dẫn đầu ra
    output_dir = request.output_dir or str(DEFAULT_OUTPUT_DIR / "character_label_data")
    memory_dir = request.memory_dir or str(DEFAULT_OUTPUT_DIR / "context_memory_data")
    character_personality_output_dir = request.character_personality_output_dir or str(DEFAULT_OUTPUT_DIR / "character_personality_data")
    validate_identity_character_personality_output_dir = request.validate_identity_character_personality_output_dir or str(DEFAULT_OUTPUT_DIR / "validated_character_personality_data")
    final_identity_character_dir = request.final_identity_character_dir or str(DEFAULT_OUTPUT_DIR / "personality_mapper_data/mapped_character-VA")
    character_voice_mapper_dir = request.character_voice_mapper_dir or str(DEFAULT_OUTPUT_DIR / "personality_mapper_data")
    
    # Chạy task trong background thread
    thread = threading.Thread(
        target=run_label_data_task,
        args=(task_id, input_id, {
            "input_data": request.input_data,
            "output_dir": output_dir,
            "memory_dir": memory_dir,
            "character_personality_output_dir": character_personality_output_dir,
            "validate_identity_character_personality_output_dir": validate_identity_character_personality_output_dir,
            "final_identity_character_dir": final_identity_character_dir,
            "voice_personality_dir": request.voice_personality_dir,
            "voice_personality_by_lore_dir": request.voice_personality_by_lore_dir,
            "character_voice_mapper_dir": character_voice_mapper_dir
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

@app.get("/input-status/{input_id}")
async def get_input_status(input_id: str):
    """Kiểm tra trạng thái theo input_id"""
    with TASK_LOCK:
        task_id = INPUT_ID_TASK_MAP.get(input_id)
        if task_id and task_id in TASK_DB:
            return TASK_DB[task_id]
        return {"status": "available", "input_id": input_id}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)