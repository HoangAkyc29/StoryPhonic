from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="text-to-speech-service")

# Đường dẫn base
BASE_DIR = Path(__file__).parent.parent

@app.post("/generate-emotion-audio")
async def generate_emotion_audio(
    narrative_annotation_dir: str = Form(...),
    emotion_audio_dir: Optional[str] = Form(None),
    transcript_emotion_dir: Optional[str] = Form(None),
    output_dir: Optional[str] = Form(None)
):
    """
    Endpoint để tạo audio với emotion từ dữ liệu đầu vào
    
    Parameters:
    - narrative_annotation_dir: Đường dẫn đến thư mục chứa dữ liệu annotation (bắt buộc)
    - emotion_audio_dir: Thư mục chứa audio emotion mẫu (nếu không có sẽ dùng mặc định)
    - transcript_emotion_dir: Thư mục chứa transcript emotion (nếu không có sẽ dùng mặc định)
    - output_dir: Thư mục đầu ra (nếu không có sẽ dùng mặc định)
    """
    try:
        # Xử lý các đường dẫn
        default_data_dir = BASE_DIR / "reference_voice_data"
        default_output_dir = BASE_DIR / "temporary_output_voice_data" / "text_to_speech"
        
        emotion_audio_dir = emotion_audio_dir or str(default_data_dir / "emotion_voices")
        transcript_emotion_dir = transcript_emotion_dir or str(default_data_dir / "emotion_voices_transcript")
        output_dir = output_dir or str(default_output_dir)

        logger.info(f"Starting TTS with emotion processing...")
        logger.info(f"Input directory: {narrative_annotation_dir}")
        
        # Gọi hàm chính từ module
        from process_generate_emotion_audio import generate_all_TTS_with_emotion
        
        result_dir = generate_all_TTS_with_emotion(
            narrative_annotation_dir=narrative_annotation_dir,
            emotion_audio_dir=emotion_audio_dir,
            transcript_emotion_dir=transcript_emotion_dir,
            output_dir=output_dir
        )
        
        logger.info(f"Completed processing. Output directory: {result_dir}")
        
        return JSONResponse({
            "status": "success",
            "output_dir": result_dir,
            "message": "Emotion audio generated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error in generate_emotion_audio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate emotion audio: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "text-to-speech"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)