from scipy.spatial.distance import euclidean
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import re
import json
import unicodedata
from collections import defaultdict
from .model_loader import sentence_transformer_model_loader

sentence_transformer_model = sentence_transformer_model_loader()

DEFAULT_CROWD_CHARACTER = {
    "traits": {
        "Compliant": 0.6,
        "Average": 0.7,
        "Agreeable": 0.5,
        "Passive": 0.4
    }
}

def get_character_embedding(character_data: dict, model) -> np.ndarray:
    """
    Calculates trait embedding.  Uses default traits for crowd characters
    if data is missing or invalid, or if any weight is invalid.
    """
    trait_embeddings = []
    trait_weights = []
    use_default = False

    if not character_data["traits"]:
        use_default = True
    else:
        for trait, weight in character_data["traits"].items():
            try:
                weight = float(weight)
                if weight < 0:
                    use_default = True  # Use default if any weight is negative
                    break
            except:
                use_default = True  # Use default if any weight is invalid
                break
        if use_default:
            print("Warning: Invalid weight found. Using default crowd character traits.")


    if use_default:
        character_data = DEFAULT_CROWD_CHARACTER


    for trait, weight in character_data["traits"].items():
        try:
            weight = float(weight)
            if weight < 0:
                continue # Skip negative weights (shouldn't happen now, but just in case)
            embedding = model.encode(trait, convert_to_tensor=False)
            trait_embeddings.append(embedding)
            trait_weights.append(weight)
        except:
            continue # Skip invalid traits/weights

    trait_embeddings = np.array(trait_embeddings)
    trait_weights = np.array(trait_weights, dtype=float)

    if trait_weights.sum() == 0:
        return np.zeros(model.encode("").shape) # Return zero vector if no valid weights

    return np.average(trait_embeddings, axis=0, weights=trait_weights)

def calculate_similarity(char1_data, char2_data, model, age_weight = 0.4, OCEAN_weight = 0.3, trait_weight = 0.3):
    """
    Calculates the overall similarity between two characters with custom weights.

    Args:
        char1_data (dict): Data for the first character.
        char2_data (dict): Data for the second character.
        model (SentenceTransformer): The Sentence Transformer model.
        age_weight (float): Weight for age similarity.
        OCEAN_weight (float): Weight for OCEAN similarity.
        trait_weight (float): Weight for trait similarity.

    Returns:
        float: The overall similarity score.
    """

    # 1. Age similarity
    age_diff = abs(char1_data["age"] - char2_data["age"])
    max_age_diff = 100
    age_similarity = 1 - (age_diff / max_age_diff)

    # 2. OCEAN similarity (Euclidean distance)
    OCEAN1 = np.array([char1_data["OCEAN"][trait] for trait in "OCEAN"])
    OCEAN2 = np.array([char2_data["OCEAN"][trait] for trait in "OCEAN"])
    OCEAN_distance = euclidean(OCEAN1, OCEAN2)
    max_OCEAN_distance = np.sqrt(20)
    OCEAN_similarity = 1 - (OCEAN_distance / max_OCEAN_distance)

    # 3. Trait similarity (cosine similarity)
    traits1 = get_character_embedding(char1_data, model)
    traits2 = get_character_embedding(char2_data, model)
    trait_similarity = cosine_similarity([traits1], [traits2])[0][0]

    # 4. Weighted average of similarities
    overall_similarity = (
        age_weight * age_similarity
        + OCEAN_weight * OCEAN_similarity
        + trait_weight * trait_similarity
    )
    return overall_similarity

def find_n_most_similar_in_group_b(
    characters_a, characters_b, model, output_path = None, age_weight = 0.4, OCEAN_weight = 0.3, trait_weight = 0.3, n=10
):
    """
    Finds the N most similar characters in group B for each character in group A.

    Args:
        characters_a (dict): Dictionary of characters in group A.
        characters_b (dict): Dictionary of characters in group B.
        model (SentenceTransformer): The Sentence Transformer model.
        output_path : the path to json file that save the results data
        age_weight (float): Weight for age similarity.
        OCEAN_weight (float): Weight for OCEAN similarity.
        trait_weight (float): Weight for trait similarity.
        n (int): The number of similar characters to return for each character in A.

    Returns:
        dict: A dictionary where keys are character names from group A,
              and values are lists of tuples (character_name_from_B, similarity_score),
              sorted by similarity.
    """
    # Input validation (example)
    if not isinstance(characters_a, dict) or not isinstance(characters_b, dict):
        raise TypeError("characters_a and characters_b must be dictionaries.")
    if not isinstance(age_weight, float) or not isinstance(OCEAN_weight, float) or not isinstance(trait_weight, float):
        raise TypeError("Weights must be floats.")
    if not np.isclose(age_weight + OCEAN_weight + trait_weight, 1.0):  # Use np.isclose for float comparison
        raise ValueError("Weights must sum to 1.0.")
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer.")
    
    n = min(len(characters_b),n)
    results = {}
    for char_a_name, char_a_data in characters_a.items():
        similarities = []
        for char_b_name, char_b_data in characters_b.items():
            # Check gender
            if char_a_data["gender"] != char_b_data["gender"]:
                continue

            similarity = calculate_similarity(
                char_a_data, char_b_data, model, age_weight, OCEAN_weight, trait_weight
            )
            similarities.append((char_b_name, similarity))

        # Sort by similarity and take top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        results[char_a_name] = similarities[:n]

    if output_path:
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4) # Sử dụng indent để file JSON dễ đọc hơn

    return results


def create_fit_format_input_data(
    character_personality_output_dir: str,
    voice_personality_dir: str,
    voice_personality_by_lore_dir: str,
):
    """
    Creates input data in the correct format for character similarity analysis.

    Args:
        character_personality_output_dir (str): Directory containing JSON files
            for characters in characters_a.
        voice_personality_dir (str): Directory containing JSON files with age information
            for characters in characters_b.  Files are named the same as those in
            voice_personality_by_lore_dir.
        voice_personality_by_lore_dir (str): Directory containing JSON files
            for characters in characters_b (OCEAN, traits, gender).

    Returns:
        tuple[dict | None, dict | None]: A tuple containing characters_a and characters_b
            in the correct format, or (None, None) if an error occurs.
    """

    characters_a = {}
    characters_b = {}

    # --- Xử lý characters_a ---
    for filename in os.listdir(character_personality_output_dir):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(character_personality_output_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading or parsing {filename}: {e}")
            return None, None

        character_name = filename[:-5].lower()
        characters_a[character_name] = {
            "gender": data["character_identity"]["gender"].lower(),  # Lowercase for consistency
            "age": age if isinstance(age := data["character_identity"].get("approximate_age"), (int, float)) and age is not None and age != "" else 25,
            "OCEAN": {
                "O": data["personality_traits"]["openness"],
                "C": data["personality_traits"]["conscientiousness"],
                "E": data["personality_traits"]["extraversion"],
                "A": data["personality_traits"]["agreeableness"],
                "N": data["personality_traits"]["neuroticism"],
            },
            "traits": {
                trait["adjective"].lower(): trait["weight"]
                for trait in data["core_personality_adjectives"]
            },
        }

    # --- Xử lý characters_b ---
    for filename in os.listdir(voice_personality_by_lore_dir):
        if not filename.endswith(".json"):
            continue

        filepath_lore = os.path.join(voice_personality_by_lore_dir, filename)
        filepath_voice = os.path.join(voice_personality_dir, filename)

        try:
            with open(filepath_lore, "r", encoding="utf-8") as f_lore:
                lore_data = json.load(f_lore)
            with open(filepath_voice, "r", encoding="utf-8") as f_voice:
                voice_data = json.load(f_voice)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading or parsing {filename} (lore or voice): {e}")
            continue

        character_name = lore_data["character_info"]["name"]

        # 1. Get the age, parse from voice_data
        age_str = voice_data["speaker_info"]["age"]
        age = 25 #default age is 20
        # Age range: extract numbers and calculate the average
        try:
            matches = re.findall(r'\d+', age_str)  # Find all digits
            if len(matches) == 2:
                age = (int(matches[0]) + int(matches[1])) / 2
            elif len(matches) == 1:
                age = int(matches[0])

        except (ValueError, TypeError):
            print(f"Warning: Could not parse age range for {character_name}: {age_str}")

        # 2. Build the character data

        # Get OCEAN scores, try both key names.  Use get() to avoid KeyError
        OCEAN_assessment = lore_data.get("OCEAN_assessment") or lore_data.get("OCEAN_assessment (personality traits)")
        if not OCEAN_assessment:
            print(f"Warning: Skipping {character_name} due to missing OCEAN assessment.")
            continue  # Skip if OCEAN assessment is missing

        characters_b[character_name] = {
            "gender": lore_data["character_info"]["gender"].lower(),  # Lowercase for consistency
            "age": age,
            "OCEAN": {
                "O": OCEAN_assessment["Openness"]["score"],
                "C": OCEAN_assessment["Conscientiousness"]["score"],
                "E": OCEAN_assessment["Extraversion"]["score"],
                "A": OCEAN_assessment["Agreeableness"]["score"],
                "N": OCEAN_assessment["Neuroticism"]["score"],
            },
            "traits": {
                trait["adjective"].lower(): trait["weight"]
                for trait in lore_data["core_personality_adjectives"]
            },
        }

    return characters_a, characters_b

def personality_mapper_main(character_personality_output_dir = r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\character_personality_data\constant_id_2",
                            voice_personality_dir = r"D:\FINAL_CODE\backend\modules\task_3\reference_voice_data\character_personality_mapping",
                            voice_personality_by_lore_dir = r"D:\FINAL_CODE\backend\modules\task_3\reference_voice_data\character_personality_mapping_by_lore",
                            model = sentence_transformer_model,
                            output_path = r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\personality_mapper_data\constant_id_2.json",
                            age_weight = 0.4, OCEAN_weight = 0.3, trait_weight = 0.3, n=20):
    characters_a, characters_b = create_fit_format_input_data(character_personality_output_dir, voice_personality_dir, voice_personality_by_lore_dir)
    return find_n_most_similar_in_group_b(characters_a,characters_b,sentence_transformer_model,output_path,age_weight,OCEAN_weight,trait_weight,n)

# personality_mapper_main()

def create_unique_mapping(input_json_path = r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\personality_mapper_data\constant_id_2.json", 
                          output_json_path = r"D:\FINAL_CODE\backend\modules\task_1\temporary_context_data\personality_mapper_data\mapped_character-VA\constant_id_2.json"):
    # Đọc dữ liệu từ file JSON
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tạo danh sách tất cả các cặp (outliner, similar, score, top_position)
    all_pairs = []
    
    for outliner, similar_list in data.items():
        if not similar_list:  # Bỏ qua các outliner không có similar character
            continue
        for top_pos, (similar, score) in enumerate(similar_list, start=1):
            all_pairs.append({
                'outliner': outliner,
                'similar': similar,
                'score': score,
                'top_pos': top_pos
            })
    
    # Sắp xếp các cặp theo tiêu chí ưu tiên:
    # 1. Vị trí top (top_pos) thấp hơn (ưu tiên hơn)
    # 2. Score cao hơn
    all_pairs.sort(key=lambda x: (x['top_pos'], -x['score']))
    
    # Tạo mapping và theo dõi các similar character đã được chọn
    mapping = {}
    used_similar = set()
    
    for pair in all_pairs:
        outliner = pair['outliner']
        similar = pair['similar']
        
        # Nếu outliner đã có mapping thì bỏ qua
        if outliner in mapping:
            continue
        
        # Nếu similar chưa được dùng
        if similar not in used_similar:
            mapping[outliner] = similar
            used_similar.add(similar)
    
    # Lưu kết quả ra file JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)
    
    return mapping

# personality_mapper_main()
# create_unique_mapping()


def normalize_string(s):
    """Chuẩn hóa string bằng cách:
    1. Chuyển về lowercase
    2. Loại bỏ dấu (unicode normalization)
    3. Loại bỏ tất cả ký tự không phải chữ cái, số hoặc khoảng trắng
    4. Thay nhiều khoảng trắng thành 1 khoảng trắng
    5. Strip khoảng trắng ở đầu/cuối
    """
    if not isinstance(s, str):
        return ""
    
    # Chuyển về dạng NFKD để tách dấu và ký tự
    s = unicodedata.normalize('NFKD', s)
    
    # Loại bỏ dấu và chuyển về ASCII
    s = s.encode('ascii', 'ignore').decode('ascii')
    
    # Loại bỏ tất cả ký tự đặc biệt, chỉ giữ chữ cái, số và khoảng trắng
    s = re.sub(r'[^\w\s]', '', s)
    
    # Thay nhiều khoảng trắng thành 1 khoảng trắng
    s = re.sub(r'\s+', ' ', s)
    
    # Loại bỏ khoảng trắng đầu/cuối và chuyển về lowercase
    return s.strip().lower()


def add_voice_actors(narrative_path, voice_mapping_path):
    # Đọc file mapping voice actor
    with open(voice_mapping_path, 'r', encoding='utf-8') as f:
        voice_mapping = json.load(f)
    
    # Chuẩn bị normalized mapping để tra cứu
    normalized_mapping = {
        normalize_string(character): voice_actor 
        for character, voice_actor in voice_mapping.items()
    }
    
    # Duyệt qua từng file trong narrative_path
    for filename in os.listdir(narrative_path):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(narrative_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            narrative_data = json.load(f)
        
        # Duyệt qua từng record
        for record in narrative_data:
            if "3rd" in record.get("type", "").lower():
                record["voice_actor"] = "Narrator"
                continue
            character_name = record.get("identity", "")
            normalized_name = normalize_string(character_name)
            
            # Tìm voice actor tương ứng
            original_key = normalized_mapping.get(normalized_name)
            record["voice_actor"] = voice_mapping.get(original_key, "None")
        
        # Lưu lại file đã cập nhật
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(narrative_data, f, ensure_ascii=False, indent=4)