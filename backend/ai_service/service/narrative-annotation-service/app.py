import os
import uuid
import logging
import uvicorn
from fastapi import FastAPI, HTTPException # Form và JSONResponse không được dùng trực tiếp, có thể bỏ
from pydantic import BaseModel
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
import threading
from dotenv import load_dotenv
# from collections import defaultdict # defaultdict không được dùng, có thể bỏ

# Load biến môi trường từ file .env ngoài cùng project
load_dotenv(dotenv_path=Path(__file__).resolve().parents[4] / '.env.root')

# Lấy đường dẫn tuyệt đối từ biến môi trường
data_dir_absolute = os.getenv('DATA_DIR_ABSOLUTE')
if not data_dir_absolute:
    raise ValueError("DATA_DIR_ABSOLUTE must be set in .env file")

# BASE_DIR là thư mục chứa file app.py này (thư mục gốc của dự án)
BASE_DIR = Path(__file__).resolve().parent

# Suy ra DEFAULT_OUTPUT_DIR từ DATA_DIR_ABSOLUTE
DEFAULT_OUTPUT_DIR = Path(data_dir_absolute) / "context_data"
DEFAULT_OUTPUT_VOICE_DIR = Path(data_dir_absolute) / "voice_data" / "reference_voice_data"

# Cấu hình Logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "generate_label_data_errors.log"

# Thiết lập logger riêng cho tác vụ generate_label_data
task_logger = logging.getLogger("generate_label_data_task") # Giữ nguyên tên logger
task_logger.setLevel(logging.ERROR)

file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - TaskID: %(task_id)s - InputID: %(input_id)s - Message: %(message)s')
file_handler.setFormatter(formatter)

if not task_logger.handlers:
    task_logger.addHandler(file_handler)

# --- THAY ĐỔI 2: Cập nhật import từ package 'src' ---
# Giả sử file generate_label_data.py nằm trong package 'src'
# và 'src' có file __init__.py
from src.generate_label_data import generate_label_data_main, set_cancel_flag


app = FastAPI(title="Narrative Annotation Service with Task Control")

TASK_DB: Dict[str, dict] = {}
INPUT_ID_TASK_MAP: Dict[str, str] = {}
TASK_LOCK = threading.Lock()

class TaskRequest(BaseModel):
    input_data: str
    input_id: str
    output_dir: Optional[str] = None
    memory_dir: Optional[str] = None
    character_personality_output_dir: Optional[str] = None
    validate_identity_character_personality_output_dir: Optional[str] = None
    final_identity_character_dir: Optional[str] = None
    voice_personality_dir: Optional[str] = None
    voice_personality_by_lore_dir: Optional[str] = None
    character_voice_mapper_dir: Optional[str] = None
    text_input_data_dir: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    input_id: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    result_dirs: Optional[dict] = None
    message: Optional[str] = None

def run_label_data_task(task_id: str, input_id: str, request_data: dict):
    """Hàm xử lý dài hạn chạy trong background"""
    try:
        with TASK_LOCK:
            TASK_DB[task_id]["status"] = "running"
            TASK_DB[task_id]["start_time"] = datetime.now().isoformat()

        # generate_label_data_main đã được import từ src ở đầu file
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
            character_voice_mapper_dir=request_data["character_voice_mapper_dir"],
            text_input_data_dir=request_data["text_input_data_dir"]
        )

        with TASK_LOCK:
            if result_dirs is None:
                TASK_DB[task_id]["status"] = "cancelled"
                TASK_DB[task_id]["message"] = "Task was cancelled by user"
            else:
                TASK_DB[task_id]["status"] = "completed"
                TASK_DB[task_id]["result_dirs"] = {
                    "label_data_dir": result_dirs[0],
                    "personality_data_dir": result_dirs[1],
                    "final_identity_dir": result_dirs[2]
                }
            TASK_DB[task_id]["end_time"] = datetime.now().isoformat()
            if INPUT_ID_TASK_MAP.get(input_id) == task_id:
                del INPUT_ID_TASK_MAP[input_id]

    except Exception as e:
        error_message = f"Error in generate_label_data_main: {str(e)}"
        task_logger.error(
            error_message,
            exc_info=True,
            extra={'task_id': task_id, 'input_id': input_id}
        )
        with TASK_LOCK:
            TASK_DB[task_id]["status"] = "failed"
            TASK_DB[task_id]["message"] = str(e)
            TASK_DB[task_id]["end_time"] = datetime.now().isoformat()
            if INPUT_ID_TASK_MAP.get(input_id) == task_id:
                del INPUT_ID_TASK_MAP[input_id]

@app.post("/generate-label-data", response_model=TaskStatus)
async def create_label_data_task(request: TaskRequest):
    input_id = request.input_id

    with TASK_LOCK:
        if input_id in INPUT_ID_TASK_MAP:
            existing_task_id = INPUT_ID_TASK_MAP[input_id]
            existing_task_details = TASK_DB.get(existing_task_id)
            if existing_task_details and isinstance(existing_task_details, dict) and \
               existing_task_details.get("status") in ["pending", "running"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Input ID '{input_id}' is already being processed by task {existing_task_id}"
                )

        task_id = str(uuid.uuid4())
        task_info = TaskStatus(
            task_id=task_id,
            input_id=input_id,
            status="pending",
            start_time=datetime.now().isoformat()
        )
        TASK_DB[task_id] = task_info.model_dump() if hasattr(task_info, 'model_dump') else task_info.dict()
        INPUT_ID_TASK_MAP[input_id] = task_id

    # Xử lý các đường dẫn đầu ra (sử dụng DEFAULT_OUTPUT_DIR đã được cập nhật)
    output_dir_str = request.output_dir or str(DEFAULT_OUTPUT_DIR / "character_label_data")
    memory_dir_str = request.memory_dir or str(DEFAULT_OUTPUT_DIR / "context_memory_data")
    character_personality_output_dir_str = request.character_personality_output_dir or str(DEFAULT_OUTPUT_DIR / "character_personality_data")
    validate_identity_character_personality_output_dir_str = request.validate_identity_character_personality_output_dir or str(DEFAULT_OUTPUT_DIR / "validated_character_personality_data")
    final_identity_character_dir_str = request.final_identity_character_dir or str(DEFAULT_OUTPUT_DIR / "personality_mapper_data/mapped_character-VA")
    character_voice_mapper_dir_str = request.character_voice_mapper_dir or str(DEFAULT_OUTPUT_DIR / "personality_mapper_data")
    text_input_data_dir_str = request.text_input_data_dir or str(DEFAULT_OUTPUT_DIR / "text_input_data")
    voice_personality_dir_str = request.voice_personality_dir or str(DEFAULT_OUTPUT_VOICE_DIR / "character_personality_mapping")
    voice_personality_by_lore_dir_str = request.voice_personality_by_lore_dir or str(DEFAULT_OUTPUT_VOICE_DIR / "character_personality_mapping_by_lore")

    thread = threading.Thread(
        target=run_label_data_task,
        args=(task_id, input_id, {
            "input_data": request.input_data,
            "output_dir": output_dir_str, # Đổi tên biến để tránh trùng với biến request
            "memory_dir": memory_dir_str,
            "character_personality_output_dir": character_personality_output_dir_str,
            "validate_identity_character_personality_output_dir": validate_identity_character_personality_output_dir_str,
            "final_identity_character_dir": final_identity_character_dir_str,
            "voice_personality_dir": voice_personality_dir_str,
            "voice_personality_by_lore_dir": voice_personality_by_lore_dir_str,
            "character_voice_mapper_dir": character_voice_mapper_dir_str,
            "text_input_data_dir": text_input_data_dir_str
        })
    )
    thread.start()

    return TASK_DB[task_id]

@app.get("/task-status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    task_data = TASK_DB.get(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatus(**task_data)

@app.get("/input-status/{input_id}")
async def get_input_status(input_id: str):
    with TASK_LOCK:
        task_id = INPUT_ID_TASK_MAP.get(input_id)
        if task_id:
            task_data = TASK_DB.get(task_id)
            if task_data:
                return TaskStatus(**task_data)
        return {"status": "available", "input_id": input_id, "message": "No active task for this input_id."}

@app.post("/cancel-task/{input_id}")
async def cancel_task(input_id: str):
    """Cancel a running task by input_id"""
    with TASK_LOCK:
        task_id = INPUT_ID_TASK_MAP.get(input_id)
        if not task_id:
            raise HTTPException(status_code=404, detail="No active task found for this input_id")
        
        task_data = TASK_DB.get(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")
            
        if task_data["status"] not in ["pending", "running"]:
            raise HTTPException(status_code=400, detail=f"Task is already {task_data['status']}")
            
        # Set cancel flag in generate_label_data.py
        set_cancel_flag(input_id)
        return {"message": "Cancel request received", "task_id": task_id, "input_id": input_id}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)