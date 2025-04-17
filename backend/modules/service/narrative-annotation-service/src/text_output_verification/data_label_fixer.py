import json
import os
import re
from ..other_service import clean_json
from .compare_sentence import compare_and_match

def process_texts(text_x, text_y, model):
    """
    Processes Text_X and Text_Y to create a mapping and update Text_Y's characters.

    Args:
        text_x: The input Text_X string.
        text_y: The input Text_Y string.

    Returns:
        The updated Text_Y JSON data with character names mapped.
    """


    # 1. Clean and load JSON data
    json_x = clean_json(text_x)
    json_y = clean_json(text_y)

    # 2. Create arrays A and B from Text_X
    chunk_index = json_x["chunk_index"]
    try:
        characters_x = json_x["characters"]
    except Exception as e:
        characters_x = json_x["updated_characters"]

    A = []
    B = []
    for char_name, char_data in characters_x.items():
        last_appearance = char_data["last_appearance_index"]
        if chunk_index - 3 <= last_appearance <= chunk_index + 3:
            A.append(char_name)
            B.append(char_name)  # Add the main name
            for alias in char_data["aliases"]:
                if alias not in B: # Prevent duplicate
                  B.append(alias)


    # 3. Create array C from Text_Y
    C = []
    for item in json_y:
        char_name = item["character"].strip()
        if "3rd" not in item["type"] and char_name not in C:
            C.append(char_name)

    # 4. Create character mapping
    character_mapping = {}
    for char_c in C:
        match_result = compare_and_match(char_c, A, B, model)
        character_mapping[char_c] = match_result[1]

    # 5. Update Text_Y with mapping
    for item in json_y:
        if "3rd" not in item["type"]:
            original_char = item["character"].strip()
            if original_char in character_mapping:
                item["character"] = character_mapping[original_char]

    return json.dumps(json_y, ensure_ascii=False, indent=4)

def get_unique_characters(directory_path, character_names_in_last_context_memory_list):
    """
    Đọc tất cả các file .txt trong thư mục chỉ định, trích xuất danh sách các nhân vật
    và trả về một danh sách các nhân vật duy nhất (không trùng lặp).

    Args:
        directory_path: Đường dẫn đến thư mục chứa các file .txt.

    Returns:
        Một danh sách các chuỗi, mỗi chuỗi là tên của một nhân vật duy nhất.
        Trả về một danh sách rỗng nếu không tìm thấy file .txt nào hoặc nếu có lỗi xảy ra.
    """
    keywords = ["unnamed", "unknown", "unidentified"]
    character_names_in_last_context_memory_list = [name.strip().lower() for name in character_names_in_last_context_memory_list]
    character_data = {}
    try:
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                filepath = os.path.join(directory_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        for item in data:
                            character = item.get("character")
                            sentence_type = item.get("type")
                            if any(keyword in character.lower() for keyword in keywords) and all(character.strip().lower() != character_name_in_last_context_memory_list for character_name_in_last_context_memory_list in character_names_in_last_context_memory_list):
                                if character not in character_data:
                                    character_data[character] = filename
                                    continue

                                while character in character_data:
                                    if character_data[character] == filename:
                                        break
                                    match = re.search(r'--(\d+)$', character)
                                    if match:
                                        new_number = int(match.group(1)) + 1
                                        character = re.sub(r'--\d+$', f'--{new_number}', character)
                                    else:
                                        character = f"{character}--1"
                                character_data[character] = filename
                                continue

                            if character and "3rd" not in sentence_type and character not in character_data:
                                character_data[character] = filename  # Lưu tên file đầu tiên
                    except json.JSONDecodeError:
                        print(f"Lỗi giải mã JSON trong file: {filename}")
                    except Exception as e:
                        print(f"Lỗi khi xử lý file {filename}: {e}")
    except FileNotFoundError:
        print(f"Thư mục không tồn tại: {directory_path}")
        return {}
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        return {}

    return character_data


def process_all_label_text_files(model, output_dir: str, memory_dir: str):
    # Lấy danh sách file trong hai thư mục
    output_files = set(os.listdir(output_dir))
    memory_files = set(os.listdir(memory_dir))
    
    # Tìm các file trùng tên
    common_files = output_files & memory_files

    matched_files = []
    for file_name in common_files:
        match = re.match(r"(.+)_(\d+)\.txt", file_name)
        if match:
            base_name = match.group(1)
            index = int(match.group(2))
            matched_files.append((file_name, base_name, index))

    if not matched_files:
        return None  # No matching files found

    # Find the file with the highest index
    highest_index_file = max(matched_files, key=lambda item: item[2])
    highest_index_filename = highest_index_file[0]
    last_memory_path = os.path.join(memory_dir, highest_index_filename)
    with open(last_memory_path, "r", encoding="utf-8") as last_memory_file:
        last_memory_content = last_memory_file.read()
    
    for filename in common_files:
        output_path = os.path.join(output_dir, filename)
        memory_path = os.path.join(memory_dir, filename)
        
        with open(output_path, "r", encoding="utf-8") as output_file, open(memory_path, "r", encoding="utf-8") as memory_file:
            output_content = output_file.read()
            memory_content = memory_file.read()
            output_content = process_texts(memory_content, output_content, model)
            output_content = process_texts(last_memory_content, output_content, model)

        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(output_content)  # Ghi đè bằng nội dung từ memory_file
