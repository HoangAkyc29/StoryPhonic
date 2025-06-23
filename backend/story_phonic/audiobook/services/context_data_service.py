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
from audiobook.models.character import Character

def get_context_data_paths(novel_id: str) -> Tuple[Path, Path, Path, Path]:
    """
    Get paths for character label data, text input data, context memory data, and validated character personality data
    """
    data_dir = Path(get_data_dir())
    base_path = data_dir / "context_data"
    
    return (
        base_path / "character_label_data" / str(novel_id),
        base_path / "text_input_data" / str(novel_id),
        base_path / "context_memory_data" / str(novel_id),
        base_path / "validated_character_personality_data" / str(novel_id)
    )

def clean_character_identity(ci: dict) -> dict:
    """Chuẩn hóa trường character_identity như logic import_validated_character_personality"""
    ci = dict(ci) if ci else {}
    for field in ["name", "aliases", "raw_name", "confidence_score"]:
        if field in ci:
            ci.pop(field)
    if "confirmed_identity" in ci and isinstance(ci["confirmed_identity"], list):
        ci["confirmed_identity"] = ci["confirmed_identity"][0] if ci["confirmed_identity"] else None
    return ci

def process_validated_character_personality(novel, validated_char_dir):
    """Đọc validated character personality json và lưu vào model Character cho novel"""
    if not validated_char_dir.exists():
        return
    json_files = list(validated_char_dir.glob("*.json"))
    for json_file in json_files:
        character_name = json_file.stem
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # --- Chuẩn hóa character_identity ---
                ci = data.get("character_identity", {})
                data["character_identity"] = clean_character_identity(ci)
                character_info = json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error reading {json_file}: {str(e)}")
            continue
        # Tìm index tiếp theo cho character trong novel
        with transaction.atomic():
            existing = Character.objects.filter(novel=novel, name=character_name, is_deleted=False).first()
            if existing:
                continue
            next_index = (Character.objects.filter(novel=novel).count() + 1)
            Character.objects.create(
                novel=novel,
                name=character_name,
                character_info=character_info,
                index=next_index
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
        char_label_path, text_input_path, context_memory_path, validated_char_dir = get_context_data_paths(novel_id)
        
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

        # --- Process validated character personality ---
        process_validated_character_personality(novel, validated_char_dir)
        # --- END ---
        
        return True
        
    except Novel.DoesNotExist:
        print(f"Novel with id {novel_id} not found")
        return False
    except Exception as e:
        print(f"Error processing context data: {str(e)}")
        return False 