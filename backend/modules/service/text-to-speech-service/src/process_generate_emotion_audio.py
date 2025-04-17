import os
import sys
import json
from typing import List, Dict

def create_ref_data(audio_dir: str, text_dir: str) -> List[Dict[str, str]]:
    """
    Tạo danh sách ref_data từ thư mục audio và text
    
    Args:
        audio_dir: Đường dẫn thư mục chứa file audio .mp3
        text_dir: Đường dẫn thư mục chứa file text .txt
    
    Returns:
        List[Dict]: Danh sách các item với keys: 'ref_name', 'ref_audio', 'ref_text'
    """
    ref_data = []
    
    # Lấy danh sách file audio
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    
    for audio_file in audio_files:
        # Lấy tên file không có đuôi
        base_name = os.path.splitext(audio_file)[0]
        
        # Tạo đường dẫn đầy đủ cho file audio
        audio_path = os.path.join(audio_dir, audio_file)
        
        # Tạo tên file text tương ứng
        text_file = f"{base_name}.txt"
        text_path = os.path.join(text_dir, text_file)
        
        # Kiểm tra xem file text có tồn tại không
        if not os.path.exists(text_path):
            continue  # Bỏ qua nếu không có file text tương ứng
        
        # Đọc nội dung file text
        with open(text_path, 'r', encoding='utf-8') as f:
            text_content = f.read().strip()
        
        # Tạo dictionary cho item hiện tại
        ref_item = {
            'ref_name': base_name,
            'ref_audio': audio_path,
            'ref_text': text_content
        }
        
        ref_data.append(ref_item)
    
    return ref_data


def load_text_data_from_json_dir(json_dir: str) -> List[List[Dict[str, str]]]:
    """
    Đọc các file JSON từ thư mục và tạo text_data theo định dạng yêu cầu
    
    Args:
        json_dir: Đường dẫn thư mục chứa các file JSON
    
    Returns:
        List[List[Dict]]: Dữ liệu văn bản với cấu trúc phù hợp
    """
    text_data = []
    
    # Lấy danh sách tất cả file JSON trong thư mục
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json') and '_' in f]
    
    # Sắp xếp file theo số thứ tự {i} trong tên file
    json_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    for json_file in json_files:
        file_path = os.path.join(json_dir, json_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                
                # Kiểm tra và chuyển đổi cấu trúc dữ liệu
                if isinstance(file_data, list):
                    processed_item = []
                    for sentence in file_data:
                        # Đảm bảo có đủ các trường cần thiết
                        processed_sentence = {
                            'sentence': sentence.get('sentence', ''),
                            'emotion': sentence.get('emotion', 'neutral'),
                            'voice_actor': sentence.get('voice_actor', 'default'),
                            'gender': str(sentence.get('gender', 'female')).lower()
                        }
                        processed_item.append(processed_sentence)
                    
                    text_data.append(processed_item)
                
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Warning: Could not load {json_file}: {str(e)}")
            continue
    
    return text_data

def generate_all_TTS_with_emotion(narrative_annotation_dir = r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\character_label_data\constant_id_4",
                                  emotion_audio_dir = r".\reference_voice_data\emotion_voices",
                                  transcript_emotion_dir = r".\reference_voice_data\emotion_voices_transcript",
                                  output_dir = r".\temporary_output_voice_data\text_to_speech"):
    
    emotion_audio_dir = os.path.abspath(emotion_audio_dir)
    transcript_emotion_dir = os.path.abspath(transcript_emotion_dir)
    output_dir = os.path.abspath(output_dir)
    last_folder_name = os.path.basename(narrative_annotation_dir)

    output_dir = os.path.join(output_dir, last_folder_name)

    ref_data = create_ref_data(emotion_audio_dir,transcript_emotion_dir)
    text_data = load_text_data_from_json_dir(narrative_annotation_dir)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Đi vào 2 cấp (để đến thư mục F5-TTS)
    f5_tts_dir = os.path.join(current_dir, 'F5-TTS')

    # Gán đường dẫn đến thư mục F5-TTS\src
    f5_tts_src_dir = os.path.join(f5_tts_dir, 'src')

    # Thêm đường dẫn vào sys.path
    sys.path.insert(0, f5_tts_src_dir)

    import f5_tts
    from f5_tts import multi_input_multi_ref_run_inference

    multi_input_multi_ref_run_inference(ref_data,text_data,output_dir,last_folder_name)
    
    return output_dir

# generate_all_TTS_with_emotion()