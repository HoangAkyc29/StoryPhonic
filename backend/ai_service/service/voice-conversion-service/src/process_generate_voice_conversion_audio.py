import os
import json
import re
import sys
from typing import Dict

def normalize_string(s: str) -> str:
    """Chuẩn hóa chuỗi để so sánh: lowercase, bỏ dấu, bỏ khoảng trắng thừa và ký tự đặc biệt"""
    # Chuyển thành chữ thường
    s = s.lower()
    # Loại bỏ các dấu câu và ký tự đặc biệt (giữ lại chữ cái, số và khoảng trắng)
    s = re.sub(r'[^\w\s]', '', s)
    # Loại bỏ khoảng trắng thừa và thay thế khoảng trắng bằng dấu gạch dưới
    s = re.sub(r'\s+', '_', s.strip())
    return s

def find_audio_mapping(audio_dir3: str, json_dir: str, audio_dir1: str, narrator_gender = 0) -> Dict[str, str]:
    """
    Tạo mapping giữa các file audio trong thư mục 3 với các file audio tương ứng trong thư mục 1
    
    Args:
        audio_dir3: Đường dẫn thư mục chứa các file audio .wav (có va_string_name trong tên)
        json_dir: Đường dẫn thư mục chứa các file json annotation
        audio_dir1: Đường dẫn thư mục chứa các file audio .wav gốc
        
    Returns:
        Dict[str, str]: Mapping từ đường dẫn file audio trong thư mục 3 sang đường dẫn file audio tương ứng trong thư mục 1
    """
    # Bước 1: Đọc tất cả các file json và tạo mapping từ character name đến json file name
    json_name_to_character = {}
    character_to_json_name = {}
    
    for json_file in os.listdir(json_dir):
        if not json_file.endswith('.json'):
            continue
            
        json_path = os.path.join(json_dir, json_file)
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                character_name = data['character_info']['name']
                normalized_character = normalize_string(character_name)
                json_name = os.path.splitext(json_file)[0]
                character_to_json_name[normalized_character] = json_name
                json_name_to_character[json_name] = normalized_character
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {json_file}: {e}")
                continue
    
    # Bước 2: Tạo danh sách các file audio trong thư mục 1 (chỉ lấy tên không có đuôi)
    audio1_files = set()
    audio1_normalized_map = {}
    
    for audio_file in os.listdir(audio_dir1):
        if not audio_file.endswith('.wav'):
            continue
        audio_name = os.path.splitext(audio_file)[0]
        audio1_files.add(audio_name)
        normalized_audio = normalize_string(audio_name)
        audio1_normalized_map[normalized_audio] = audio_name
    
    # Bước 3: Xử lý từng file trong thư mục 3 và tạo mapping
    mapping = {}
    
    for audio3_file in os.listdir(audio_dir3):
        if not audio3_file.endswith('.wav'):
            continue
            
        audio3_path = os.path.join(audio_dir3, audio3_file)
        
        # Trích xuất va_string_name từ tên file
        # Giả sử định dạng là ..._{va_string_name}.wav
        base_name = os.path.splitext(audio3_file)[0]
        va_string = base_name.split('_')[-1]  # Lấy phần cuối sau dấu _
        if (normalize_string(va_string) == "narrator" or normalize_string(va_string) == "none") and narrator_gender == 0:
            va_string = "Jing Yuan"
        elif (normalize_string(va_string) == "narrator" or normalize_string(va_string) == "none") and narrator_gender == 1:
            va_string = "Ningguang"
        normalized_va = normalize_string(va_string)
        
        # Bước 3a: Tìm trong character_info của các json file
        matched_audio1 = None
        
        if normalized_va in character_to_json_name:
            json_name = character_to_json_name[normalized_va]
            # Tìm file audio trong thư mục 1 có tên trùng với json_name
            if json_name in audio1_files:
                matched_audio1 = os.path.join(audio_dir1, json_name + '.wav')
            else:
                # Thử tìm bằng normalized version
                normalized_json_name = normalize_string(json_name)
                if normalized_json_name in audio1_normalized_map:
                    original_name = audio1_normalized_map[normalized_json_name]
                    matched_audio1 = os.path.join(audio_dir1, original_name + '.wav')
        
        # Bước 3b: Nếu không tìm thấy qua json, thử tìm trực tiếp trong thư mục 1
        if not matched_audio1:
            # Tìm xem có file audio nào trong thư mục 1 có normalized name chứa normalized_va
            for normalized_audio, original_name in audio1_normalized_map.items():
                if normalized_va in normalized_audio:
                    matched_audio1 = os.path.join(audio_dir1, original_name + '.wav')
                    break
        
        if matched_audio1:
            mapping[audio3_path] = matched_audio1
        else:
            print(f"Warning: Could not find match for {audio3_file}")
            mapping[audio3_path] = None
    
    return mapping

def generate_end_output_audio(audio_dir3 = r"D:\FINAL_CODE\backend\ai_service\data\voice_data\temporary_output_voice_data\text_to_speech", 
                              json_dir = r"D:\FINAL_CODE\backend\ai_service\data\voice_data\reference_voice_data\character_personality_mapping_by_lore", 
                              audio_dir1 = r"D:\FINAL_CODE\backend\ai_service\data\voice_data\reference_voice_data\character_voices",
                              output_dir = r"D:\FINAL_CODE\backend\ai_service\data\voice_data\temporary_output_voice_data\voice_conversion",
                              config_path = r".\seed-vc\configs\presets\config_dit_mel_seed_uvit_whisper_base_f0_44k.yml",
                              checkpoint_path = r".\ai_model\DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema.pth",
                              narrator_gender = 0, #0 là mặc định male, 1 là female
                              constant_id = "constant_id_4"):
    # Args:
    #     audio_dir3: Đường dẫn thư mục chứa các file audio .wav (có va_string_name trong tên)
    #     json_dir: Đường dẫn thư mục chứa các file json annotation
    #     audio_dir1: Đường dẫn thư mục chứa các file audio .wav gốc
        
    audio_dir3  = os.path.abspath(audio_dir3)
    audio_dir1  = os.path.abspath(audio_dir1)
    json_dir    = os.path.abspath(json_dir)
    output_dir  = os.path.abspath(output_dir)
    checkpoint_path = os.path.abspath(checkpoint_path)
    config_path = os.path.abspath(config_path)

    audio_dir3 = os.path.join(audio_dir3,constant_id)
    output_dir = os.path.join(output_dir,constant_id)

    mapping_data = find_audio_mapping(audio_dir3,json_dir,audio_dir1, narrator_gender)

    args_dict = {
    "mapping_json": mapping_data,
    "output": output_dir,
    "diffusion_steps": 50,
    "length_adjust": 1.0,
    "inference_cfg_rate": 0.7,
    "f0_condition": False,
    "auto_f0_adjust": True,
    "semi_tone_shift": 0,
    "checkpoint_path": checkpoint_path,
    "config_path": config_path,
    "fp16": True
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Đi vào 1 cấp (để đến thư mục F5-TTS)
    seed_vc_dir = os.path.join(current_dir, 'seed-vc')

    # Thêm đường dẫn vào sys.path
    sys.path.insert(0, seed_vc_dir)

    import inference
    from inference import main_generate_multifile_voice_conversion

    main_generate_multifile_voice_conversion(args_dict)

    return output_dir

generate_end_output_audio()
# Example usage:
# if __name__ == "__main__":
#     audio_dir1 = "path/to/audio/dir1"  # Thay bằng đường dẫn thực tế
#     json_dir = "path/to/json/dir"      # Thay bằng đường dẫn thực tế
#     audio_dir3 = "path/to/audio/dir3"  # Thay bằng đường dẫn thực tế
    
#     mapping = find_audio_mapping(audio_dir3, json_dir, audio_dir1)
    
#     # Lưu kết quả ra file JSON
#     output_path = "audio_mapping.json"
#     with open(output_path, 'w', encoding='utf-8') as f:
#         json.dump(mapping, f, indent=2, ensure_ascii=False)
    
#     print(f"Mapping completed. Results saved to {output_path}")