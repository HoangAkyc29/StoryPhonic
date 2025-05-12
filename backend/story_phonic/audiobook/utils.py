import os
from pathlib import Path
from django.conf import settings
import shutil
from dotenv import load_dotenv

def get_data_dir():
    """Get the absolute path to the data directory from .env.root"""
    # Get current file's directory (audiobook)
    current_dir = Path(__file__).parent
    # Go up 2 levels to reach project root
    project_root = current_dir.parent.parent
    # Get .env.root path
    env_path = project_root / '.env.root'
    
    if not env_path.exists():
        raise FileNotFoundError(".env.root file not found")
    
    # Load environment variables from .env.root
    load_dotenv(env_path)
    data_dir = os.getenv('DATA_DIR_ABSOLUTE')
    
    if not data_dir:
        raise ValueError("DATA_DIR_ABSOLUTE not found in .env.root")
    
    return data_dir

def save_novel_file(novel_id, file):
    """Save uploaded file to the novel's directory"""
    # Get base data directory
    data_dir = get_data_dir()
    
    # Create novel directory path
    novel_dir = Path(data_dir) / "text_input_data" / str(novel_id)
    novel_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file using chunks for memory efficiency
    file_path = novel_dir / file.name
    with open(file_path, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    return str(file_path)

def read_file_content(file_path):
    """Read content from file based on its extension"""
    file_path = Path(file_path)
    if file_path.suffix.lower() == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_path.suffix.lower() == '.pdf':
        # TODO: Implement PDF reading
        # For now, return empty string
        return ""
    elif file_path.suffix.lower() == '.docx':
        # TODO: Implement DOCX reading
        # For now, return empty string
        return ""
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}") 