from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import os
import uuid
from generate_label_data import generate_label_data_main
from pathlib import Path
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="narrative-annotation-service")

# Đường dẫn mặc định (có thể override bằng biến môi trường)
BASE_DIR = Path(__file__).parent.parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "context_data"

@app.post("/generate-label-data")
async def generate_label_data(
    input_data: str = Form(...),
    input_id: Optional[str] = Form(None),
    output_dir: Optional[str] = Form(None),
    memory_dir: Optional[str] = Form(None),
    character_personality_output_dir: Optional[str] = Form(None),
    validate_identity_character_personality_output_dir: Optional[str] = Form(None),
    final_identity_character_dir: Optional[str] = Form(None),
    voice_personality_dir: Optional[str] = Form(None),
    voice_personality_by_lore_dir: Optional[str] = Form(None),
    character_voice_mapper_dir: Optional[str] = Form(None)
):
    """
    Endpoint để gọi hàm generate_label_data_main với các tham số đầu vào
    
    Parameters:
    - input_data: Dữ liệu đầu vào (bắt buộc)
    - input_id: ID duy nhất cho request (nếu không có sẽ tự sinh)
    - Các tham số đường dẫn khác: Nếu không có sẽ dùng giá trị mặc định
    """
    try:
        # Xử lý input_id
        request_id = input_id if input_id else str(uuid.uuid4())
        
        # Xử lý các đường dẫn đầu ra
        output_dir = output_dir or str(DEFAULT_OUTPUT_DIR / "character_label_data")
        memory_dir = memory_dir or str(DEFAULT_OUTPUT_DIR / "context_memory_data")
        character_personality_output_dir = character_personality_output_dir or str(DEFAULT_OUTPUT_DIR / "character_personality_data")
        validate_identity_character_personality_output_dir = validate_identity_character_personality_output_dir or str(DEFAULT_OUTPUT_DIR / "validated_character_personality_data")
        final_identity_character_dir = final_identity_character_dir or str(DEFAULT_OUTPUT_DIR / "personality_mapper_data/mapped_character-VA")
        character_voice_mapper_dir = character_voice_mapper_dir or str(DEFAULT_OUTPUT_DIR / "personality_mapper_data")
        
        # Gọi hàm chính
        logger.info(f"Starting processing for request ID: {request_id}")
        
        result_dirs = generate_label_data_main(
            input_data=input_data,
            input_id=request_id,
            output_dir=output_dir,
            memory_dir=memory_dir,
            character_personality_output_dir=character_personality_output_dir,
            validate_identity_character_personality_output_dir=validate_identity_character_personality_output_dir,
            final_identity_character_dir=final_identity_character_dir,
            voice_personality_dir=voice_personality_dir,
            voice_personality_by_lore_dir=voice_personality_by_lore_dir,
            character_voice_mapper_dir=character_voice_mapper_dir
        )
        
        logger.info(f"Completed processing for request ID: {request_id}")
        
        return JSONResponse({
            "status": "success",
            "request_id": request_id,
            "result_dirs": {
                "label_data_dir": result_dirs[0],
                "personality_data_dir": result_dirs[1],
                "final_identity_dir": result_dirs[2]
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)