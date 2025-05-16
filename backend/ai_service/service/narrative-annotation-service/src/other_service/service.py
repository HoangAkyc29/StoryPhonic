import os
import re
import json
from dotenv import load_dotenv

def read_file_content(file_path):
    """Đọc nội dung tệp và trả về dưới dạng chuỗi."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {file_path} không tồn tại.")   
        return None

def split_path(file_path):
    """
    Splits a file path into its folder path and file name components.

    Args:
        file_path: The path to the file (string).

    Returns:
        A tuple containing (folder_path, file_name).  Returns (None, None) if the
        path is invalid or only a file name is provided.
    """
    try:
        folder_path, file_name = os.path.split(file_path)
        return folder_path, file_name
    except AttributeError:
        print("Invalid file path provided.")
        return None, None

# Hàm cập nhật giá trị của current_context_summary đầu tiên
def update_first_context_summary(text):
    try:
        match_1 = re.search(r'"chunk_index": (\d+)', text)
        if match_1:
            # If the chunk_index is found, increment it by 1
            text = re.sub(r'"chunk_index": (\d+)', lambda m: f'"chunk_index": {int(m.group(1)) + 1}', text)

        match_2 = re.search(r'"recent_summaries":\s*\[(.*?)\]', text, re.DOTALL)
        if match_2:
            # Lấy nội dung danh sách recent_summaries
            summaries_content = match_2.group(1)
            
            # Chia danh sách thành các phần tử
            summaries = re.findall(r'"(.*?)"', summaries_content)
            
            # Cập nhật danh sách: xóa phần tử cuối và thêm "Unknown" vào đầu
            if summaries:
                summaries.pop()  # Xóa phần tử cuối
                summaries.insert(0, "Unknown")  # Thêm "Unknown" vào đầu
            
            # Chuyển danh sách thành chuỗi JSON
            updated_summaries = ", ".join(f'"{summary}"' for summary in summaries)
            
            # Thay thế nội dung recent_summaries trong text
            updated_text = re.sub(r'"recent_summaries":\s*\[.*?\]', f'"recent_summaries": [{updated_summaries}]', text, flags=re.DOTALL)
            return updated_text
        
        return text
    
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return text
    

def get_adjacent_text_chunks(folder_path, file_name):
    match = re.match(r"(.+)_(\d+)\.txt", file_name)

    if not match:
        raise ValueError("Invalid file name format")
    
    a, b = match.group(1), int(match.group(2))
    preceding_texts, following_texts = [], []
    
    for offset in [-3, -2, -1, 1, 2, 3]:
        adjacent_b = b + offset
        adjacent_file = f"{a}_{adjacent_b}.txt"
        adjacent_path = os.path.join(folder_path, adjacent_file)
        
        if os.path.exists(adjacent_path):
            with open(adjacent_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if offset < 0:
                    preceding_texts.append(content)
                else:
                    following_texts.append(content)
    
    preceding_text_chunk = "\n".join(preceding_texts) if preceding_texts else "None"
    following_text_chunk = "\n".join(following_texts) if following_texts else "None"
    
    return preceding_text_chunk, following_text_chunk

def clean_file_and_save_json_file(input_file, output_file):
    # Đọc nội dung file
    with open(input_file, "r", encoding="utf-8") as f:
        data = f.read().strip()

    # Loại bỏ phần đầu và cuối nếu có
    if data.startswith("```json"):
        data = data[len("```json"):].strip()
    if data.endswith("```"):
        data = data[:-3].strip()

    # Chuyển đổi chuỗi thành JSON
    json_data = json.loads(data)

    # Lưu lại dưới dạng file JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)



def clean_json(text):
    """
    Làm sạch chuỗi JSON bằng cách loại bỏ phần đầu và cuối không phải JSON,
    cũng như loại bỏ text trước dấu '[' hoặc '{' đầu tiên và sau dấu ']' hoặc '}' cuối cùng.
    """
    text = text.strip()

    # Loại bỏ phần đầu và cuối nếu có
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    if text.endswith("```<|eot_id|>"):
        end_len = 0 - len("```<|eot_id|>")
        text = text[:end_len].strip()

    # Tìm vị trí dấu '[' hoặc '{' đầu tiên
    start_match = re.search(r"[\{\[]", text)
    if start_match:
        start_index = start_match.start()
        text = text[start_index:]

    # Tìm vị trí dấu ']' hoặc '}' cuối cùng
    end_match = re.search(r"[\}\]]$", text) # Tìm ở cuối chuỗi
    if end_match:
        end_index = end_match.end()
        text = text[:end_index]

    return json.loads(text)

def get_last_sentence(json_data):
    """
    Extracts the last sentence from a list of JSON objects.

    Args:
        json_data: A list of dictionaries, where each dictionary represents
                   a sentence and its associated metadata.  Each dictionary
                   is expected to have a "sentence" key.

    Returns:
        The value of the "sentence" key in the last dictionary in the list.
        Returns None if the input list is empty or if the last element
        doesn't have a "sentence" key.
    """
    if not json_data:  # Check if the list is empty
        return None

    last_item = json_data[-1]  # Get the last element

    if "sentence" in last_item:
        return last_item["sentence"]
    else:
        return None

def merge_context_memory(old_context_text, update_context_text):
    print("Merge context memory...")
    old_context_memory = clean_json(old_context_text)
    update_context_memory = clean_json(update_context_text)
    # Lấy chunk_index và recent_summaries từ update_context_memory
    new_context_memory = {
        "chunk_index": update_context_memory["chunk_index"],
        "recent_summaries": update_context_memory["recent_summaries"],
        "characters": {}
    }
    
    # Copy dữ liệu từ old_context_memory
    old_characters = old_context_memory.get("characters", {})
    if old_characters == {}:
        old_characters = old_context_memory.get("updated_characters", {})

    updated_characters = update_context_memory.get("updated_characters", {})
    
    # Merge dữ liệu
    merged_characters = {}
    
    # Thêm hoặc cập nhật nhân vật từ updated_characters
    for char_name, char_data in updated_characters.items():
        merged_characters[char_name] = char_data
    
    # Giữ lại các nhân vật cũ không bị cập nhật
    for char_name, char_data in old_characters.items():
        if char_name not in updated_characters and not any(
            alias in updated_characters for alias in char_data.get("aliases", [])
        ):
            merged_characters[char_name] = char_data
    
    # Gán danh sách nhân vật hợp nhất vào new_context_memory
    new_context_memory["characters"] = merged_characters
    
    return json.dumps(new_context_memory, indent=4, ensure_ascii=False)

def truncate_description(json_data):
    try:
        # Duyệt qua tất cả các nhân vật trong dictionary "characters"
        for character in json_data["characters"].values():
            # Lấy brief_description
            description = character.get("brief_description", "")
            
            # Chia description thành các câu dựa trên dấu chấm
            sentences = description.split('.')
            
            # Lọc bỏ các câu rỗng (có thể xuất hiện nếu có nhiều dấu chấm liên tiếp)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Chỉ lấy tối đa 3 câu đầu tiên
            get_index = min(6,len(sentences))
            truncated_sentences = sentences[:get_index]
            
            # Ghép lại thành chuỗi mới, thêm dấu chấm sau mỗi câu (trừ câu cuối cùng nếu nó là câu cuối trong đoạn gốc)
            new_description = '. '.join(truncated_sentences)
            if new_description and description.endswith('.'):
                new_description += '.'
            
            # Cập nhật lại brief_description
            character["brief_description"] = new_description
    
    except Exception as e:
        print(f"Error while truncating data {e}")
    
    return json_data


def revert_update_context_memory(current_context_path, previous_context_path):
    """
    Updates the context memory by comparing the current and previous context files.

    Args:
        current_context_path (str): Path to the current context JSON file.
        previous_context_path (str): Path to the previous context JSON file.

    Returns:
        str: Updated context memory in JSON string format.
    """

    with open(current_context_path, 'r', encoding='utf-8') as f:
        current_context = json.load(f)

    with open(previous_context_path, 'r', encoding='utf-8') as f:
        previous_context = json.load(f)
    
    current_context = truncate_description(current_context)
    previous_context = truncate_description(previous_context)

    updated_memory = {
        "chunk_index": current_context["chunk_index"],
        "recent_summaries": current_context["recent_summaries"],
        "updated_characters": {}
    }

    current_characters = current_context["characters"]
    previous_characters = previous_context["characters"]

    for char_name, char_data in current_characters.items():
        if char_name not in previous_characters:
            # New character
            updated_memory["updated_characters"][char_name] = char_data
        else:
            # Check for updates
            if char_data != previous_characters[char_name]:
                updated_memory["updated_characters"][char_name] = char_data

    # Check for characters that exist in previous but not in current (removed characters)
    # Not required based on the prompt, but good to consider for a complete solution
    # removed_characters = set(previous_characters.keys()) - set(current_characters.keys())
    # for char_name in removed_characters:
    #     updated_memory["updated_characters"][char_name] = None  # Or a specific "removed" flag

    # Convert current_context back to JSON string
    current_context_json = json.dumps(current_context, indent=4, ensure_ascii=False)

    return current_context_json

def delete_small_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):  # Kiểm tra nếu là file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if len(content) < 2:  # File rỗng hoặc có ít hơn 2 ký tự
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

def is_small_file(file_path):
    if not os.path.isfile(file_path):
        return True  # Không phải file -> Trả về False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) < 30:
            os.remove(file_path)
            return True  # Trả về True nếu số ký tự < 30
        else:
            return False
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False # Nếu lỗi, không thể kiểm tra -> Trả về False
    
def text_to_json(text):
    # Chuyển dictionary thành chuỗi JSON
    json_result = json.loads(text)
    
    return json_result

def split_text_chunk_by_line(text_chunk, last_sentence):
    """
    Splits a text chunk into two parts based on the line containing the last sentence.

    Args:
        text_chunk: The original text chunk (string).
        last_sentence: The last sentence (string).

    Returns:
        A tuple containing two strings:
        - The part of the text chunk *up to and including* the line with the last sentence.
        - The remaining part of the text chunk *after* that line.
        Returns (None, None) if the last_sentence is not found.
    """

    def preprocess(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    processed_last_sentence = preprocess(last_sentence)
    lines = text_chunk.splitlines()  # Split into lines
    processed_lines = [preprocess(line) for line in lines] # Preprocess each line

    found_line_index = -1
    for i, line in enumerate(processed_lines):
        if processed_last_sentence in line:
            found_line_index = i
            break  # Stop searching after the first match

    if found_line_index == -1:
        return text_chunk, None  # Last sentence not found

    part1 = "\n".join(lines[:found_line_index + 1])  # Include the line with the sentence
    part2 = "\n".join(lines[found_line_index + 1:])

    return part1, part2

def chunk_content_tuning(current_chunk, following_text_chunk, answer_content):
    try:
        json_answer_content = clean_json(answer_content)
        last_sentence = get_last_sentence(json_answer_content)
        current_chunk, transfer_chunk = split_text_chunk_by_line(current_chunk, last_sentence)
        if transfer_chunk is not None:
            following_text_chunk = f"{transfer_chunk}\n{following_text_chunk}"
    except Exception as e:
        print(f"error when checking and tuning chunk text with its answer content: {e}")
        return None, None
        
    return current_chunk, following_text_chunk

def load_gemini_keys():
    load_dotenv("keys.env")
    gemini_keys_from_env = os.getenv('GEMINI_KEYS').split(',') if os.getenv('GEMINI_KEYS') else []
    return gemini_keys_from_env

def extract_json_response(text):
    """
    Trích xuất chuỗi JSON từ văn bản, bắt đầu sau phần "### Response:".

    Args:
        text: Văn bản đầu vào có chứa chuỗi JSON và các phần khác.

    Returns:
        Chuỗi JSON được trích xuất, hoặc None nếu không tìm thấy "### Response:".
    """
    match = re.search(r"### Response:\s*(.*)", text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None
    

def convert_txt_directory_to_json(directory):
    """Chuyển đổi tất cả file .txt trong thư mục thành file .json."""
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            txt_path = os.path.join(directory, filename)
            json_path = os.path.join(directory, filename.replace(".txt", ".json"))

            try:
                # Đọc nội dung file .txt
                with open(txt_path, "r", encoding="utf-8") as file:
                    text = file.read()

                # Làm sạch và chuyển đổi thành JSON
                data = clean_json(text)

                # Ghi dữ liệu vào file .json
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json.dump(data, json_file, indent=4, ensure_ascii=False)

                # Xóa file .txt sau khi chuyển đổi thành công
                # os.remove(txt_path)
                print(f"Converted: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

def merge_sentences(directory):
    files = sorted(
        [f for f in os.listdir(directory) if re.match(r"(.+)_\d+\.json", f)],
        key=lambda x: int(re.match(r"(.+)_(\d+)\.json", x).group(2))  # Sửa ".txt" thành ".json"
    )
    
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        merged_data = []
        prev_obj = None
        
        first_person_pronouns = {"i", "me", "my", "mine", "we", "us", "our", "ours"}
        print(f"Xử lý file {file_name}")

        for obj in data:
            # Kiểm tra nếu câu có đại từ ngôi thứ nhất và type chứa "3rd"
            if ("3rd" in obj["type"] and 
                any(word in obj["sentence"].lower().split() for word in first_person_pronouns) and 
                "narrator" not in obj["character"].lower()):
                obj["type"] = "1st-Person Narration"

            if prev_obj:
                if (
                    ("3rd" in obj["type"] and "3rd" in prev_obj["type"]) or
                    ("3rd" not in obj["type"] and obj["type"] == prev_obj["type"] and 
                    obj["character"] == prev_obj["character"] and obj["emotion"] == prev_obj["emotion"])
                ):
                    prev_obj["sentence"] += " " + obj["sentence"]
                else:
                    merged_data.append(prev_obj)
                    prev_obj = obj
            else:
                prev_obj = obj
        
        if prev_obj:
            merged_data.append(prev_obj)
        
        for index, obj in enumerate(merged_data):
            obj["index"] = index
        
        output_path = os.path.join(directory, file_name)
        with open(output_path, 'w', encoding='utf-8') as out_file:
            json.dump(merged_data, out_file, indent=4, ensure_ascii=False)
        
        print(f"Processed and saved: {output_path}")

def extract_character_names(json_file_path):
    """
    Extracts a list of character names and aliases from a JSON file.

    Args:
        json_file_path: The path to the JSON file.

    Returns:
        A list of character names and aliases.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            data = clean_json(text)

            if not data.get("characters") and data.get("updated_characters"):
                # Nếu cả hai điều kiện trên đúng, thực hiện gán
                data["characters"] = data["updated_characters"]
                
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return []
        
    character_names = []
    for character, details in data["characters"].items():
        character_names.append(character)
        if "aliases" in details:
            character_names.extend(details["aliases"])
    return character_names

def find_largest_suffix_file(directory):
    largest_number = -1
    largest_file = None
    pattern = re.compile(r"^(.+)_([0-9]+)\.txt$")  # Bắt tên file có dạng bất kỳ trước _, số, rồi .txt
    
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            number = int(match.group(2))  # Lấy phần số cuối cùng
            if number > largest_number:
                largest_number = number
                largest_file = filename
    
    return os.path.join(directory, largest_file) if largest_file else None

# convert_txt_directory_to_json(r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\character_label_data\constant_id")
# merge_sentences(r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\character_label_data\constant_id")