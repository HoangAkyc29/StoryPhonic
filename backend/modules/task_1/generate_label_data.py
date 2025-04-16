from .model_loader import llama_8B_finetune_model_loader, sentence_transformer_model_loader
import os
import random
from collections import defaultdict
import threading
import re
import time
import random
import threading
import multiprocessing
import threading

import torch
# torch.cuda.empty_cache()
from transformers import AutoTokenizer, TextStreamer
from unsloth import FastLanguageModel

import google.generativeai as genai

model_name = "gemini-2.0-flash"

from .other_service import read_file_content, update_first_context_summary, get_adjacent_text_chunks, merge_context_memory, delete_small_files, is_small_file, clean_json, extract_json_response, load_gemini_keys, merge_sentences, convert_txt_directory_to_json, extract_character_names, find_largest_suffix_file
from .character_info_summarization import answer_update_context_memory_with_gemini, get_context_memory_input_query, get_context_memory_prompt
from .dialogue_analyzer import answer_dialogue_analyzer_with_gemini, get_dialogue_analyzer_input_query, get_dialogue_analyzer_prompt
from .data_loader_and_text_chunking import save_text_chunk
from .text_output_verification import process_texts, get_unique_characters, process_all_label_text_files, process_directory_fixing_emotion
from .extract_character_personality import create_character_analysis_prompts
from .validate_character_identity import process_json_files_merging_same_character, process_narrative_data
from .character_voice_mapper import add_voice_actors, personality_mapper_main, create_unique_mapping

context_memory_instruction = get_context_memory_prompt()
dialogue_analyzer_instruction = get_dialogue_analyzer_prompt()


alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

llama_8B_model, llama_8B_tokenizer = llama_8B_finetune_model_loader()
sentence_transformer_model = sentence_transformer_model_loader()
EOS_TOKEN = llama_8B_tokenizer.eos_token # Must add EOS_TOKEN
text_streamer = TextStreamer(llama_8B_tokenizer)

def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        # Must add EOS_TOKEN, otherwise your generation will go on forever!
        text = alpaca_prompt.format(instruction, input, output) + EOS_TOKEN
        texts.append(text)
    return { "text" : texts, }

def generate_answer_with_llama_finetune(
    model,
    tokenizer,
    instruction,
    input_text,
    prompt = alpaca_prompt,
    max_new_tokens = 4096,
    top_p = 0.8,
    temperature = 0.1,
    min_p = 0.1,
    device = "cuda",
):
    """
    Generates an answer from a language model based on a given prompt, instruction, and input.

    Args:
        model: The language model (e.g., Llama).  Assumes it has a `generate` method.
        tokenizer: The tokenizer for the language model.
        prompt (str): The format string for the prompt.  Should include placeholders for instruction, input, and output.
        instruction (str): The instruction for the model.
        input_text (str): The input text for the model.
        max_new_tokens (int, optional): The maximum number of tokens to generate. Defaults to 16000.
        top_p (float, optional): The top-p sampling parameter. Defaults to 0.8.
        temperature (float, optional): The temperature sampling parameter. Defaults to 0.1.
        min_p (float, optional): The min-p sampling parameter. Defaults to 0.1.
        device (str, optional): The device to run the model on ("cuda" or "cpu"). Defaults to "cuda".

    Returns:
        str: The generated answer from the model.
    """

    # Prepare the input
    formatted_prompt = prompt.format(
        instruction,  # instruction
        input_text,  # input
        "",  # output - leave this blank for generation!
    )

    inputs = tokenizer([formatted_prompt], return_tensors="pt").to(device)

    # Generate the output
    # Disable gradient calculation for inference
    with torch.no_grad():
        outputs = model.generate(
                **inputs,
                streamer = text_streamer,
                max_new_tokens=max_new_tokens,
                use_cache=True,
                top_p=top_p,
                temperature=temperature,
                min_p=min_p,
                eos_token_id=tokenizer.eos_token_id
            )

    # Decode the output
    decoded_output = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

    return decoded_output


def generate_answer(
    input_text,
    model = None,
    tokenizer = None,
    prompt = alpaca_prompt,
    max_new_tokens = 4096,
    top_p = 0.8,
    temperature = 0.1,
    min_p = 0.1,
    gemini_key = None,
    task_code = "update_context_memory"

):

    if gemini_key == None:
        if task_code == "update_context_memory":
            return generate_answer_with_llama_finetune(model, tokenizer, context_memory_instruction, input_text, prompt, max_new_tokens, top_p, temperature, min_p)
        else:
            return generate_answer_with_llama_finetune(model, tokenizer, dialogue_analyzer_instruction, input_text, prompt, max_new_tokens, top_p, temperature, min_p)
    else:
        if task_code == "update_context_memory":
            return answer_update_context_memory_with_gemini(input_text, current_key = gemini_key)
        else:
            return answer_dialogue_analyzer_with_gemini(input_text, current_key = gemini_key)


# folder_path = đường dẫn folder chứa các chunk text của novel
# output_dir  = output cho dữ liệu của nhiệm vụ dialogue_analyzer
# memory_dir  = output cho dữ liệu của nhiệm vụ character_info_summarization
# def process_files_in_folder(folder_path = "", output_dir = "", memory_dir = "", key = None, file_name_list = []):
def process_files_in_folder(files_path, output_dir = "", memory_dir = "", key = None):
    """Xử lý tất cả các file .txt trong thư mục và lưu kết quả vào thư mục 'llm_label_answer'."""

    CONTEXT_MEMORY = "None"
    UPDATED_CONTEXT_MEMORY = "None"

    print(f"Start analyzing data....")

    error_messages = ["skipped this file", "other errors", "max rate limit"]
    retry_counter = 0
    last_memory_file_dir = None
    break_outer = False

    for file_path in files_path:
            file_name = os.path.basename(file_path)
            if break_outer == True:
                break
            output_file_path = os.path.join(output_dir, file_name)
            memory_file_path = os.path.join(memory_dir, file_name)
            last_memory_file_dir = memory_file_path
        
            if os.path.exists(memory_file_path) == True and os.path.exists(output_file_path) == True:
                print(f"File {file_name} đã tồn tại. Bỏ qua việc tạo tệp này.")
                continue

            # 2 biến a, b để extract info từ file_name
            a = None
            b = 0

            retry_counter = 0  # Initialize retry_counter *inside* the outer loop, for each file

            while retry_counter <= 4:  # Use a while loop for retries
                try:
                    CONTEXT_MEMORY = "None"
                    UPDATED_CONTEXT_MEMORY = "None"

                    print("Match txt files name.")
                    match = re.match(r"(.+)_(\d+)\.txt", file_name)
                    if match:
                        a = match.group(1)
                        b = int(match.group(2))

                        if b == 0:
                            CONTEXT_MEMORY = "None"

                        if b > 0 and CONTEXT_MEMORY == "None":
                            try:
                                c = b - 1
                                previous_memory_data_file_name = f"{a}_{c}.txt"
                                previous_memory_file_path = os.path.join(memory_dir, previous_memory_data_file_name)
                                with open(previous_memory_file_path, "r", encoding="utf-8") as previous_memory_file:
                                    CONTEXT_MEMORY = previous_memory_file.read()
                            except Exception as e:
                                print(f"Error while trying to read previous memory! Error: {e}")
                                os.remove(previous_memory_file_path)
                                break_outer == True
                                break  # Keep the break here, it's for a specific condition

                    input_query_update_context_memory = get_context_memory_input_query(file_path, CONTEXT_MEMORY)
                    # response_2 = answer_update_context_memory_with_gemini(file_path, choosen_model, key)
                    # if retry_counter <= 2:
                    #     response_2 = generate_answer(input_query_update_context_memory,llama_8B_model,llama_8B_tokenizer)
                    # else:
                    response_2 = generate_answer(input_query_update_context_memory, temperature=0.4, gemini_key=key)
                    response_temp = clean_json(response_2)

                    if not response_2:
                        print("There is no response 2") # Moved print statement
                        retry_counter += 1
                        continue # Added continue statement

                    if any(message in response_2.lower() for message in error_messages):
                        print("error message triggered for task 2!")
                        retry_counter += 1
                        continue # Added continue statement
                    else:
                        print(f"Finish response task 2. Start writing file task 2.")

                        if CONTEXT_MEMORY == "None":
                            CONTEXT_MEMORY = response_2
                        else:
                            UPDATED_CONTEXT_MEMORY = response_2
                            CONTEXT_MEMORY = merge_context_memory(CONTEXT_MEMORY, UPDATED_CONTEXT_MEMORY)
                            
                        with open(memory_file_path, "w", encoding="utf-8") as memory_file:
                            memory_file.write(CONTEXT_MEMORY)

                    print(f"Start prompting with task 1...")

                    input_query_dialogue_analyzer = get_dialogue_analyzer_input_query(file_path, CONTEXT_MEMORY)
                    # if retry_counter <= 2:
                    #     response_1 = generate_answer(input_query_dialogue_analyzer,llama_8B_model,llama_8B_tokenizer, task_code="dialogue analyzer")
                    #     response_1 = extract_json_response(response_1)
                    # else:
                    response_1 = generate_answer(input_query_dialogue_analyzer, gemini_key=key, task_code="dialogue analyzer")
                    
                    response_temp = clean_json(response_1)

                    if not response_1:
                        print("There is no response 1") # Moved print statement
                        retry_counter += 1
                        continue # Added continue statement

                    if any(message in response_1.lower() for message in error_messages):
                        print("error message triggered for task 1!")
                        retry_counter += 1
                        continue

                    with open(output_file_path, "w", encoding="utf-8") as output_file:
                        output_file.write(response_1)

                    print(f"Successfully create label for {file_name}")
                    retry_counter = 0  # Reset retry_counter on success
                    break_outer = False
                    break  # Exit the while loop on success

                except Exception as e:
                    print(f"Error : {e}")
                    retry_counter += 1

            if retry_counter >= 5:
                break_outer = True
                break
    
    return break_outer, last_memory_file_dir

def generate_label_data_main(input_data, output_dir = r".\task_1\temporary_context_data\character_label_data", 
                             memory_dir = r".\task_1\temporary_context_data\context_memory_data", 
                             character_personality_output_dir = r".\task_1\temporary_context_data\character_personality_data", 
                             validate_identity_character_personality_output_dir = r".\task_1\temporary_context_data\validated_character_personality_data",
                             final_identity_character_dir = r".\task_1\temporary_context_data\personality_mapper_data\mapped_character-VA",
                             voice_personality_dir = r"D:\FINAL_CODE\backend\modules\task_3\reference_voice_data\character_personality_mapping",
                             voice_personality_by_lore_dir = r"D:\FINAL_CODE\backend\modules\task_3\reference_voice_data\character_personality_mapping_by_lore",
                             character_voice_mapper_dir = r".\task_1\temporary_context_data\personality_mapper_data"):
    gemini_keys_from_env = load_gemini_keys()
    gemini_key = gemini_keys_from_env[0]
    gemini_key_len = len(gemini_keys_from_env)
    break_outer = True
    retry_counter = 0

    input_files_paths, input_id, grand_text_input = save_text_chunk(input_data)
    if input_files_paths == None:
        return
    
    # Convert relative paths to absolute paths
    output_dir = os.path.abspath(output_dir)
    memory_dir = os.path.abspath(memory_dir)
    character_personality_output_dir = os.path.abspath(character_personality_output_dir)
    validate_identity_character_personality_output_dir = os.path.abspath(validate_identity_character_personality_output_dir)
    final_identity_character_dir = os.path.abspath(final_identity_character_dir)
    character_voice_mapper_dir = os.path.abspath(character_voice_mapper_dir)

    output_dir = os.path.join(output_dir, input_id)
    memory_dir = os.path.join(memory_dir, input_id)
    character_personality_output_dir = os.path.join(character_personality_output_dir, input_id)
    validate_identity_character_personality_output_dir = os.path.join(validate_identity_character_personality_output_dir, input_id)

    final_identity_character_dir = os.path.join(final_identity_character_dir, f"{input_id}.json")
    character_voice_mapper_dir = os.path.join(character_voice_mapper_dir, f"{input_id}.json")
    
    # Tạo thư mục (bao gồm cả thư mục cha nếu chưa có)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(memory_dir, exist_ok=True)
    os.makedirs(character_personality_output_dir, exist_ok=True)
    os.makedirs(validate_identity_character_personality_output_dir, exist_ok=True)
    # os.makedirs(final_identity_character_dir, exist_ok=True)
    # os.makedirs(character_voice_mapper_dir, exist_ok=True)

    while break_outer == True and retry_counter < 3:
        break_outer,last_memory_file_dir = process_files_in_folder(input_files_paths, output_dir, memory_dir, gemini_key)
        if break_outer == True:
            retry_counter += 1

    if retry_counter < 4:
        gemini_index = 0
        un_finished_flag = True
        while gemini_index < gemini_key_len and un_finished_flag == True:
            gemini_key = gemini_keys_from_env[gemini_index]
            process_all_label_text_files(sentence_transformer_model, output_dir, memory_dir) # bước chuẩn hoá output tên nhân vật
            convert_txt_directory_to_json(output_dir) # tạo ra các output data định dạng json tương ứng với các file txt output
            merge_sentences(output_dir) #merge các sentences object có cùng speaker với cùng type và emotion
            process_directory_fixing_emotion(output_dir,sentence_transformer_model) #fix label nhãn emotion được tạo ra bởi LLM.
            character_names_in_last_context_memory_list = extract_character_names(find_largest_suffix_file(memory_dir))
            unique_characters_dict = get_unique_characters(output_dir, character_names_in_last_context_memory_list) #trích ra tổng hợp các nhân vật đã xuất hiện trong bộ truyện từ output cùng lần xuất hiện đầu tiên
            character_prompts_answer, un_finished_flag = create_character_analysis_prompts(grand_text_input,output_dir,unique_characters_dict,last_memory_file_dir,len(input_files_paths),character_personality_output_dir,gemini_key) #sinh bộ nhân cách và các thông tin khác của nhân vật từ dict trên tại character_personality_output_dir
            gemini_index += 1
    
        process_json_files_merging_same_character(character_personality_output_dir,validate_identity_character_personality_output_dir,sentence_transformer_model,0.85) #ghép các cặp nhân vật nhận diện là các cá thể khác nhau nhưng thực ra lại là cùng 1 nhân vật
        process_narrative_data(output_dir,validate_identity_character_personality_output_dir,unique_characters_dict)

        personality_mapper_main(validate_identity_character_personality_output_dir,voice_personality_dir,voice_personality_by_lore_dir, sentence_transformer_model,character_voice_mapper_dir)
        create_unique_mapping(character_voice_mapper_dir,final_identity_character_dir)
        add_voice_actors(output_dir,final_identity_character_dir)
        return output_dir, character_personality_output_dir



# generate_label_data_main(r"D:\extract_novel_character_data_llama_8B\cote_4.pdf")
generate_label_data_main(r"D:\Learning\ReZero.pdf")

# print(get_unique_characters(r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\character_label_data\constant_id"))