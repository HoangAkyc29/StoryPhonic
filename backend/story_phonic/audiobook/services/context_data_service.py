import os
import json
from pathlib import Path
from typing import Tuple
from django.db import transaction
from audiobook.models.novel import Novel
from audiobook.models.chunk_annotation import ChunkAnnotation
from audiobook.models.text_chunk import TextChunk
from audiobook.models.chunk_context_memory import ChunkContextMemory
from .file_service import get_data_dir

def get_context_data_paths(novel_id: str) -> Tuple[Path, Path, Path]:
    """
    Get paths for character label data, text input data, and context memory data
    """
    data_dir = Path(get_data_dir())
    base_path = data_dir / "context_data"
    
    return (
        base_path / "character_label_data" / str(novel_id),
        base_path / "text_input_data" / str(novel_id),
        base_path / "context_memory_data" / str(novel_id)
    )

def process_context_data(novel_id: str) -> bool:
    """
    Process and store context data from files to database
    Returns True if successful, False otherwise
    """
    try:
        # Get novel instance
        novel = Novel.objects.get(id=novel_id)
        
        # Check novel status
        if not (novel.status.startswith('error_') and int(novel.status.split('_')[1]) >= 2) and novel.status != 'completed':
            return False
            
        # Get paths
        char_label_path, text_input_path, context_memory_path = get_context_data_paths(novel_id)
        
        # Process character label data (ChunkAnnotation)
        if char_label_path.exists():
            for file in char_label_path.glob(f"{novel_id}_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        index = int(file.stem.split('_')[1])
                        
                        # Convert entire JSON data to text
                        clean_text = json.dumps(data, ensure_ascii=False, indent=4)
                        
                        ChunkAnnotation.objects.update_or_create(
                            novel=novel,
                            index=index,
                            defaults={
                                'raw_text': clean_text,
                                'clean_text': clean_text,
                                'status': 'done',
                                'is_deleted': False
                            }
                        )
                except Exception as e:
                    print(f"Error processing character label file {file}: {str(e)}")
                    continue
        
        # Process text input data (TextChunk)
        if text_input_path.exists():
            for file in text_input_path.glob(f"{novel_id}_*.txt"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        index = int(file.stem.split('_')[1])
                        
                        TextChunk.objects.update_or_create(
                            novel=novel,
                            index=index,
                            defaults={
                                'content': content,
                                'is_deleted': False
                            }
                        )
                except Exception as e:
                    print(f"Error processing text input file {file}: {str(e)}")
                    continue
        
        # Process context memory data (ChunkContextMemory)
        if context_memory_path.exists():
            for file in context_memory_path.glob(f"{novel_id}_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        index = int(file.stem.split('_')[1])
                        
                        # Convert entire JSON data to text
                        content = json.dumps(data, ensure_ascii=False, indent=4)
                        
                        ChunkContextMemory.objects.update_or_create(
                            novel=novel,
                            index=index,
                            defaults={
                                'content': content,
                                'is_deleted': False
                            }
                        )
                except Exception as e:
                    print(f"Error processing context memory file {file}: {str(e)}")
                    continue
        
        return True
        
    except Novel.DoesNotExist:
        print(f"Novel with id {novel_id} not found")
        return False
    except Exception as e:
        print(f"Error processing context data: {str(e)}")
        return False 