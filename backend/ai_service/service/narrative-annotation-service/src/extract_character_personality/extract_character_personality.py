import json
import os
import re
import time
import string
from ..other_service import read_file_content, get_adjacent_text_chunks, split_path, clean_json
import mimetypes

import google.generativeai as genai

model_gemini = "gemini-2.0-flash"

extract_personality_prompt = None

script_dir = os.path.dirname(os.path.abspath(__file__)) 
bfi_pdf_path = os.path.join(script_dir, r"Personality-BigFiveInventory_34.pdf")

def get_extract_personality_prompt (filename="extract_character_personality_prompt.txt"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename)

    # Open and read the file
    global extract_personality_prompt 
    if extract_personality_prompt  == None:
        with open(filepath, "r", encoding="utf-8") as f:
            extract_personality_prompt  = f.read()
    return extract_personality_prompt 

def upload_to_gemini(path, mime_type="application/pdf"):
    """Uploads an audio file to Gemini API and returns the file object."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded: {file.display_name} -> {file.uri}")
    return file

def find_characters_appearing_first_in_chunk(data):
    """
    Finds characters who first appear in the current chunk.

    Args:
        data: A dictionary containing the text data.

    Returns:
        A JSON string containing a list of characters who first appear in the
        current chunk, along with their information (excluding
        first_appearance_index, last_appearance_index, and number_of_appearances).
    """

    chunk_index = data["chunk_index"]
    try:
        characters = data["characters"]
    except Exception as e:
        characters = data["updated_characters"]
    if characters == None:
        characters = data["updated_characters"]
    appearing_characters = []

    for character_name, character_info in characters.items():
        if character_info["first_appearance_index"] == chunk_index:
            # Create a new dictionary without the unwanted keys
            filtered_info = {
                key: value
                for key, value in character_info.items()
                if key not in [
                    "first_appearance_index",
                    "last_appearance_index",
                    "number_of_appearances",
                ]
            }
            appearing_characters.append({character_name: filtered_info})

    return json.dumps(appearing_characters, indent=4, ensure_ascii=False)


def create_character_analysis_prompts(grand_input_text, output_dir, unique_character_list, context_memory_file_dir, len_value, character_personality_output_dir, current_key, choosen_model = model_gemini, bfi_pdf_path = bfi_pdf_path):
    """
    Generates prompts for character analysis using Gemini, based on the provided data.

    Args:
        grand_input_text (str): The entire novel text.
        output_dir (str): Path to the directory containing character label files.
        unique_character_list (dict): Dictionary mapping character names to their first appearance label files.
        context_memory_file_dir (str): Path to the context memory file.
        len_value (int): Total number of chunks the novel is divided into.
        current_key (str): Your Gemini API key.
        choosen_model (str): The name of the Gemini model to use.

    Returns:
        dict: A dictionary mapping character names to their corresponding Gemini responses.
    """

    def normalize_string(s):
        """Normalizes a string by removing punctuation, lowercasing, and removing spaces."""
        s = s.lower()
        s = s.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
        s = s.replace(" ", "")  # Remove spaces
        return s

    character_prompts = {}
    context_memory = {}
    retry_counter = 0
    un_finished = False
    with open(context_memory_file_dir, 'r', encoding="utf-8") as f:
        context_memory_text = f.read()
        context_memory = clean_json(context_memory_text)
    
    genai.configure(api_key=current_key)
                # Create the model
    generation_config = {
        "temperature": 0.1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 4096,
        "response_mime_type": "text/plain",
    }

    instruction = get_extract_personality_prompt()
                
    model = genai.GenerativeModel(
        model_name=choosen_model,
        generation_config=generation_config,
        system_instruction= instruction,
    )
    
    files = [upload_to_gemini(bfi_pdf_path)]

    for char_name, label_file in unique_character_list.items():
        print(f"Start prompting for {char_name} ...")
        retry_counter = 0
        while retry_counter < 3:
            print(f"retry number {retry_counter}")
            # Check if the file already exists
            filepath = os.path.join(character_personality_output_dir, f"{char_name.replace(' ', '_')}.json")
            if os.path.exists(filepath):
                print(f"File already exists for {char_name}. Skipping.")
                character_prompts[char_name] = "File already exists. Skipped."
                break  # Skip to the next character
            time.sleep(30)
            # 1. Character Information from Context Memory
            character_info = None
            normalized_char_name = normalize_string(char_name)
            
            if not context_memory.get("characters") and context_memory.get("updated_characters"):
                # Nếu cả hai điều kiện trên đúng, thực hiện gán
                context_memory["characters"] = context_memory["updated_characters"]

            for character, details in context_memory['characters'].items():
                normalized_character = normalize_string(character)
                if normalized_char_name == normalized_character or \
                any(normalize_string(alias) == normalized_char_name for alias in details.get('aliases', [])):
                    character_info = details
                    break

            # 2. First Appearance Data
            first_appearance_passage = ""
            first_appearance_context = ""
            relative_position = 0.0

            label_file_path = os.path.join(output_dir, label_file)
            try:
                with open(label_file_path, 'r', encoding='utf-8') as f:
                    label_data_text = f.read()
                    label_data = clean_json(label_data_text)

                character_sentences = []
                for item in label_data:
                    if item['character'] == char_name:
                        character_sentences.append(item['sentence'])
                first_appearance_passage = "\n".join(character_sentences)
                first_appearance_context = label_data_text

                match = re.match(r"(.+)_(\d+).txt", label_file)
                if match:
                    b = int(match.group(2))
                    relative_position = round(((b + 1) / (len_value + 1)) * 100)

            except FileNotFoundError:
                print(f"Warning: Label file not found for {char_name}: {label_file_path}")
                first_appearance_passage = "Not Found"
                first_appearance_context = "Not Found"
                relative_position = 0.0
                break
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON in label file for {char_name}: {label_file_path}")
                first_appearance_passage = "Invalid JSON"
                first_appearance_context = "Invalid JSON"
                relative_position = 0.0
                break

            # 3. Construct the User Prompt
            user_prompt = f"Analyze the personality traits of {char_name} based on the provided information.\n\n"
            if character_info:
                user_prompt += "Character name and information:\n"
                for key, value in character_info.items():
                    if key not in ["first_appearance_index", "last_appearance_index", "number_of_appearances"]:
                        user_prompt += f"  - {key}: {value}\n"
            else:
                user_prompt += f"Character name: {char_name}\n"

            user_prompt += "First appearance:\n"
            user_prompt += f"  - Specific passage: {first_appearance_passage}\n"
            user_prompt += f"  - Context of specific passage: {first_appearance_context}\n"
            user_prompt += f"  - Relative position of the context: {relative_position}%\n"

            user_prompt += "Provide the output in JSON format as specified in the instructions."

            # 4. Interact with Gemini
            try:

                chat_session = model.start_chat(
                    history=[
                        {"role": "user", "parts": "Novel text input:"},
                        {"role": "user", "parts": [grand_input_text]},  # Văn bản đầu vào trước
                        {"role": "user", "parts": ["PDF file containing 44 questions from The Big Five Inventory (BFI)."]},  # Đoạn mô tả ở giữa
                        {"role": "user", "parts": [files[0]]},  # Tệp PDF sau
                    ]
                )

                response = chat_session.send_message(user_prompt)
                response_test_json = clean_json(response.text)

                try:
                    if not "error" in response.text.lower() and not "exhausted" in response.text.lower():
                        with open(filepath, 'w', encoding='utf-8') as outfile:
                            json.dump(response_test_json, outfile, indent=4, ensure_ascii=False)
                        character_prompts[char_name] = filepath  # Store the filepath
                    else:
                        print(response.text)
                        un_finished = True
                    break
                except Exception as e:
                    print(f"Error writing to file for {char_name}: {e}")
                    retry_counter += 1
                    time.sleep(30)
            except Exception as e:
                print(f"Error during Gemini interaction for {char_name}: {e}")
                retry_counter += 1
                time.sleep(30)
                
        if retry_counter >= 4:
            un_finished = True

    return character_prompts, un_finished


# import json
# import os
# import re
# import time
# import string
# from ..other_service import read_file_content, get_adjacent_text_chunks, split_path, clean_json
# import google.generativeai as genai

# model_gemini = "gemini-2.0-flash"

# extract_personality_prompt = None


# def get_extract_personality_prompt (filename="extract_character_personality_prompt.txt"):
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     filepath = os.path.join(current_dir, filename)

#     # Open and read the file
#     global extract_personality_prompt 
#     if extract_personality_prompt  == None:
#         with open(filepath, "r", encoding="utf-8") as f:
#             extract_personality_prompt  = f.read()
#     return extract_personality_prompt 

# def find_characters_appearing_first_in_chunk(data):
#     """
#     Finds characters who first appear in the current chunk.

#     Args:
#         data: A dictionary containing the text data.

#     Returns:
#         A JSON string containing a list of characters who first appear in the
#         current chunk, along with their information (excluding
#         first_appearance_index, last_appearance_index, and number_of_appearances).
#     """

#     chunk_index = data["chunk_index"]
#     try:
#         characters = data["characters"]
#     except Exception as e:
#         characters = data["updated_characters"]
#     if characters == None:
#         characters = data["updated_characters"]
#     appearing_characters = []

#     for character_name, character_info in characters.items():
#         if character_info["first_appearance_index"] == chunk_index:
#             # Create a new dictionary without the unwanted keys
#             filtered_info = {
#                 key: value
#                 for key, value in character_info.items()
#                 if key not in [
#                     "first_appearance_index",
#                     "last_appearance_index",
#                     "number_of_appearances",
#                 ]
#             }
#             appearing_characters.append({character_name: filtered_info})

#     return json.dumps(appearing_characters, indent=4, ensure_ascii=False)


# def create_character_analysis_prompts(grand_input_text, output_dir, unique_character_list, context_memory_file_dir, len_value, character_personality_output_dir, current_key, choosen_model = model_gemini):
#     """
#     Generates prompts for character analysis using Gemini, based on the provided data.

#     Args:
#         grand_input_text (str): The entire novel text.
#         output_dir (str): Path to the directory containing character label files.
#         unique_character_list (dict): Dictionary mapping character names to their first appearance label files.
#         context_memory_file_dir (str): Path to the context memory file.
#         len_value (int): Total number of chunks the novel is divided into.
#         current_key (str): Your Gemini API key.
#         choosen_model (str): The name of the Gemini model to use.

#     Returns:
#         dict: A dictionary mapping character names to their corresponding Gemini responses.
#     """

#     def normalize_string(s):
#         """Normalizes a string by removing punctuation, lowercasing, and removing spaces."""
#         s = s.lower()
#         s = s.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
#         s = s.replace(" ", "")  # Remove spaces
#         return s

#     character_prompts = {}
#     context_memory = {}
#     retry_counter = 0
#     un_finished = False
#     with open(context_memory_file_dir, 'r', encoding="utf-8") as f:
#         context_memory_text = f.read()
#         context_memory = clean_json(context_memory_text)

#     for char_name, label_file in unique_character_list.items():
#         print(f"Start prompting for {char_name} ...")
#         retry_counter = 0
#         while retry_counter < 3:
#             print(f"retry number {retry_counter}")
#             time.sleep(30)
#             # Check if the file already exists
#             filepath = os.path.join(character_personality_output_dir, f"{char_name.replace(' ', '_')}.json")
#             if os.path.exists(filepath):
#                 print(f"File already exists for {char_name}. Skipping.")
#                 character_prompts[char_name] = "File already exists. Skipped."
#                 break  # Skip to the next character

#             # 1. Character Information from Context Memory
#             character_info = None
#             normalized_char_name = normalize_string(char_name)
#             for character, details in context_memory['characters'].items():
#                 normalized_character = normalize_string(character)
#                 if normalized_char_name == normalized_character or \
#                 any(normalize_string(alias) == normalized_char_name for alias in details.get('aliases', [])):
#                     character_info = details
#                     break

#             # 2. First Appearance Data
#             first_appearance_passage = ""
#             first_appearance_context = ""
#             relative_position = 0.0

#             label_file_path = os.path.join(output_dir, label_file)
#             try:
#                 with open(label_file_path, 'r', encoding='utf-8') as f:
#                     label_data_text = f.read()
#                     label_data = clean_json(label_data_text)

#                 character_sentences = []
#                 for item in label_data:
#                     if item['character'] == char_name:
#                         character_sentences.append(item['sentence'])
#                 first_appearance_passage = "\n".join(character_sentences)
#                 first_appearance_context = label_data_text

#                 match = re.match(r"(.+)_(\d+).txt", label_file)
#                 if match:
#                     b = int(match.group(2))
#                     relative_position = round(((b + 1) / (len_value + 1)) * 100)

#             except FileNotFoundError:
#                 print(f"Warning: Label file not found for {char_name}: {label_file_path}")
#                 first_appearance_passage = "Not Found"
#                 first_appearance_context = "Not Found"
#                 relative_position = 0.0
#                 break
#             except json.JSONDecodeError:
#                 print(f"Warning: Invalid JSON in label file for {char_name}: {label_file_path}")
#                 first_appearance_passage = "Invalid JSON"
#                 first_appearance_context = "Invalid JSON"
#                 relative_position = 0.0
#                 break

#             # 3. Construct the User Prompt
#             user_prompt = f"Analyze the personality traits of {char_name} based on the provided information.\n\n"
#             if character_info:
#                 user_prompt += "Character name and information:\n"
#                 for key, value in character_info.items():
#                     if key not in ["first_appearance_index", "last_appearance_index", "number_of_appearances"]:
#                         user_prompt += f"  - {key}: {value}\n"
#             else:
#                 user_prompt += f"Character name: {char_name}\n"

#             user_prompt += "First appearance:\n"
#             user_prompt += f"  - Specific passage: {first_appearance_passage}\n"
#             user_prompt += f"  - Context of specific passage: {first_appearance_context}\n"
#             user_prompt += f"  - Relative position of the context: {relative_position}%\n"

#             user_prompt += "Provide the output in JSON format as specified in the instructions."

#             # 4. Interact with Gemini
#             try:
#                 genai.configure(api_key=current_key)
#                 # Create the model
#                 generation_config = {
#                 "temperature": 0.3,
#                 "top_p": 0.95,
#                 "top_k": 40,
#                 "max_output_tokens": 4096,
#                 "response_mime_type": "text/plain",
#                 }

#                 instruction = get_extract_personality_prompt()
                
#                 model = genai.GenerativeModel(
#                 model_name=choosen_model,
#                 generation_config=generation_config,
#                 system_instruction= instruction,
#                 )

#                 chat_session = model.start_chat(
#                 history=[{"role": "user", "parts": [grand_input_text]}]
#                 )

#                 response = chat_session.send_message(user_prompt)
#                 response_test_json = clean_json(response.text)

#                 try:
#                     if not "error" in response.text.lower() and not "exhausted" in response.text.lower():
#                         with open(filepath, 'w', encoding='utf-8') as outfile:
#                             json.dump(response_test_json, outfile, indent=4, ensure_ascii=False)
#                         character_prompts[char_name] = filepath  # Store the filepath
#                     else:
#                         print(response.text)
#                         un_finished = True
#                     break
#                 except Exception as e:
#                     print(f"Error writing to file for {char_name}: {e}")
#                     retry_counter += 1
#                     time.sleep(30)
#             except Exception as e:
#                 print(f"Error during Gemini interaction for {char_name}: {e}")
#                 retry_counter += 1
#                 time.sleep(30)
                
#         if retry_counter >= 4:
#             un_finished = True

#     return character_prompts, un_finished
