import os
import time
from ..other_service import read_file_content, get_adjacent_text_chunks, split_path
import google.generativeai as genai

model_gemini = "gemini-2.0-flash"

context_memory_prompt = None

def get_context_memory_prompt(filename="character_info_summarization_prompt.txt"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename)

    # Open and read the file
    global context_memory_prompt
    if context_memory_prompt == None:
        with open(filepath, "r", encoding="utf-8") as f:
            context_memory_prompt = f.read()
    return context_memory_prompt

def get_context_memory_input_query(file_path, CONTEXT_MEMORY):
    folder_path, file_name = split_path(file_path)
    preceding_text_chunk, following_text_chunk = get_adjacent_text_chunks(folder_path, file_name)
    current_chunk = read_file_content(file_path)

        # Định dạng nội dung của user_query
    if current_chunk is not None:
        user_query = f"""PREVIOUS CONTEXT MEMORY: 
        {CONTEXT_MEMORY}

        PRECEDING TEXT CHUNK:
        {preceding_text_chunk}

        FOLLOWING TEXT CHUNK:
        {following_text_chunk}

        MAIN TEXT CHUNK:
        {current_chunk}
        """
    else:
        user_query = None

    return user_query

# file_path = đường dẫn của file text chunk hiện tại
def answer_update_context_memory_with_gemini(user_query, current_key = None, choosen_model = model_gemini):
    """Chuyển đổi nội dung tệp thành câu hỏi cho API OpenAI và trả về kết quả."""
    # Đọc nội dung từ file
    # Đọc nội dung file
        
    if not user_query:
        return {"message": "Không có nội dung để xử lý."}
    
    if not current_key:
        return {"message": "Không có key để xử lý."}

    try:
            genai.configure(api_key=current_key)
            # Create the model
            generation_config = {
            "temperature": 0.5,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
            }

            instruction = get_context_memory_prompt()
            
            model = genai.GenerativeModel(
            model_name=choosen_model,
            generation_config=generation_config,
            system_instruction= instruction,
            )

            chat_session = model.start_chat(
            history=[])

            response = chat_session.send_message(user_query)
            time.sleep(30)
            return response.text
    
    except Exception as e:
            print(f"Max rate limit for this token or other error. Error : {e}")
            with open("Errors.txt", "a", encoding="utf-8") as file:
                file.write('\n--------------------\n')
                file.write(user_query)
                file.write('\n\n')
                file.write(f"Error when answering with key {current_key} using gemini: {e}.")
                file.write('\n--------------------\n')
            time.sleep(30)

            return f"Max rate limit for this token or Other errors. Error : {e}"

