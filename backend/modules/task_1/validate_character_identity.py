import os
import json
import numpy as np
from collections import defaultdict
from sentence_transformers import util
import re
import unicodedata

from .model_loader import sentence_transformer_model_loader
sentence_transformer_model = sentence_transformer_model_loader()


class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root != y_root:
            self.parent[y_root] = x_root

def load_json_files(input_dir):
    """Load all JSON files from the input directory"""
    json_files = []
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_files.append({
                    'filename': filename,
                    'data': data
                })
    return json_files

def get_identity_strings(json_data):
    """Extract identity strings (confirmed_identity + aliases) from JSON data"""
    identity = json_data['character_identity']['confirmed_identity']
    aliases = json_data['character_identity'].get('aliases', [])
    return [identity] + aliases

def find_similar_groups(json_files, model, threshold=0.75):
    """Group JSON files that refer to the same character using Union-Find"""
    # Create a list of all identity strings with their source indices
    identity_strings = []
    for i, file_data in enumerate(json_files):
        strings = get_identity_strings(file_data['data'])
        for s in strings:
            identity_strings.append((i, s))
    
    # Encode all identity strings
    texts = [s for _, s in identity_strings]
    embeddings = model.encode(texts, convert_to_tensor=True)
    
    # Compute cosine similarity between all pairs
    cosine_scores = util.cos_sim(embeddings, embeddings)
    
    # Initialize Union-Find
    uf = UnionFind(len(json_files))
    
    # Find all similar pairs and union them
    for i in range(len(identity_strings)):
        for j in range(i+1, len(identity_strings)):
            if cosine_scores[i][j] > threshold:
                file_idx_i = identity_strings[i][0]
                file_idx_j = identity_strings[j][0]
                uf.union(file_idx_i, file_idx_j)
    
    # Group files by their root parent
    groups = defaultdict(list)
    for i in range(len(json_files)):
        root = uf.find(i)
        groups[root].append(i)
    
    return list(groups.values())

def merge_group_files(group_indices, json_files):
    """Merge JSON files in a group into a single consolidated JSON"""
    if not group_indices:
        return None
    
    merged = {
        'character_identity': {
            'name': [],
            'confirmed_identity': [],
            'aliases': [],
            'gender': None,
            'approximate_age': [],
            'confidence_score': []
        },
        'personality_traits': {
            'openness': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        },
        'core_personality_adjectives': defaultdict(list),
        'bfi_responses': defaultdict(list)
    }
    
    # First pass: collect all data
    for idx in group_indices:
        data = json_files[idx]['data']
        ci = data['character_identity']
        pt = data['personality_traits']
        cpa = data['core_personality_adjectives']
        bfi = data['bfi_responses']
        
        # Character identity
        merged['character_identity']['name'].append(ci.get('name', ''))
        merged['character_identity']['confirmed_identity'].append(ci['confirmed_identity'])
        merged['character_identity']['aliases'].extend(ci.get('aliases', []))
        
        # Handle gender (take first non-None)
        if merged['character_identity']['gender'] is None and 'gender' in ci:
            merged['character_identity']['gender'] = ci['gender']
        
        if 'approximate_age' in ci and ci['approximate_age'] is not None:
            merged['character_identity']['approximate_age'].append(ci['approximate_age'])
        if 'confidence_score' in ci and ci['confidence_score'] is not None:
            merged['character_identity']['confidence_score'].append(ci['confidence_score'])
        
        # Personality traits
        for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            if trait in pt and pt[trait] is not None:
                merged['personality_traits'][trait].append(pt[trait])
        
        # Core personality adjectives
        for adj in cpa:
            if adj['weight'] is not None:
                merged['core_personality_adjectives'][adj['adjective']].append(adj['weight'])
        
        # BFI responses
        for q, score in bfi.items():
            if score is not None:
                merged['bfi_responses'][q].append(score)
    
    # Second pass: filter None values and average numerical values
    # Character identity
    if 'approximate_age' in merged['character_identity']:
        if merged['character_identity']['approximate_age']:
            merged['character_identity']['approximate_age'] = merged['character_identity']['approximate_age'][0]
        else:
            merged['character_identity'].pop('approximate_age')
    
    if 'confidence_score' in merged['character_identity']:
        merged['character_identity']['confidence_score'] = [score for score in merged['character_identity']['confidence_score'] if score is not None]
        if merged['character_identity']['confidence_score']:
            merged['character_identity']['confidence_score'] = float(np.mean(merged['character_identity']['confidence_score']))
        else:
            merged['character_identity'].pop('confidence_score')
    
    # Personality traits
    for trait in list(merged['personality_traits'].keys()):
        merged['personality_traits'][trait] = [val for val in merged['personality_traits'][trait] if val is not None]
        if merged['personality_traits'][trait]:
            merged['personality_traits'][trait] = float(np.mean(merged['personality_traits'][trait]))
        else:
            merged['personality_traits'].pop(trait)
    
    # Core personality adjectives
    core_adjectives = []
    for adj, weights in merged['core_personality_adjectives'].items():
        weights = [w for w in weights if w is not None]
        if weights:
            core_adjectives.append({
                'adjective': adj,
                'weight': float(np.mean(weights))
            })
    merged['core_personality_adjectives'] = core_adjectives
    
    # BFI responses
    bfi_responses = {}
    for q, scores in merged['bfi_responses'].items():
        scores = [s for s in scores if s is not None]
        if scores:
            bfi_responses[q] = int(round(np.mean(scores)))
    merged['bfi_responses'] = bfi_responses
    
    return merged

def process_json_files_merging_same_character(input_dir, output_dir, model, threshold=0.75):
    """Main processing function"""
    # Load all JSON files
    json_files = load_json_files(input_dir)
    
    if not json_files:
        print("No JSON files found in the input directory.")
        return
    
    # Group similar files
    groups = find_similar_groups(json_files, model, threshold)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each group
    for i, group in enumerate(groups):
        # Merge files in the group
        merged_data = merge_group_files(group, json_files)
        
        if merged_data:
            # Save merged file
            output_filename = f"merged_character_{i+1}.json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved merged file for group {i+1} with {len(group)} files to {output_path}")


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


def process_narrative_data(narrative_path, validated_path, unique_characters_dict):
    keywords = ["unnamed", "unknown", "unidentified"]
    
    # First, load all validated character data for quick lookup
    validated_characters = {}
    characters_gender = {}
    for filename in os.listdir(validated_path):
        if filename.endswith('.json'):
            with open(os.path.join(validated_path, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                names = [normalize_string(name) for name in data['character_identity']['name']]
                gender = data['character_identity']['gender']
                validated_characters[filename[:-5]] = names  # Remove .json extension
                characters_gender[filename[:-5]] = gender    # Remove .json extension
    
    # Process each narrative file
    for filename in os.listdir(narrative_path):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(narrative_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            narrative_data = json.load(f)
        
        for record in narrative_data:
            # Check for 3rd person narration
            if "3rd" in record.get("type", "").lower():
                record["identity"] = "Narrator"
                continue
                
            # Get character name and process it
            character_name = record.get("character", "")
            processing_name = normalize_string(character_name)
            
            # Check for keywords in character name
            found_keyword = None
            for keyword in keywords:
                if keyword in processing_name:
                    found_keyword = keyword
                    break
                    
            if found_keyword:
                # Find matching name in unique_characters_dict for this file
                base_filename = filename[:-5]  # Remove .json extension
                for char_name, char_file in unique_characters_dict.items():
                    norm_char_name = normalize_string(char_name)
                    norm_char_file = normalize_string(char_file[:-5]) if char_file.endswith('.json') else normalize_string(char_file)
                    
                    if (found_keyword in norm_char_name and 
                        norm_char_file == normalize_string(base_filename)):
                        processing_name = norm_char_name
                        break
            
            # Now look for matching identity in validated characters
            record_identity = None
            record_gender = None
            for identity, names in validated_characters.items():
                if processing_name in names:
                    record_identity = identity
                    record_gender = characters_gender[identity]
                    break
            if record_gender:
                record["gender"] = record_gender
            else:
                record["gender"] = "None"
                
            if record_identity:
                record["identity"] = record_identity
            else:
                record["identity"] = "None"
        
        # Save the modified data back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(narrative_data, f, ensure_ascii=False, indent=4)
            
# input_directory = r".\task_1\temporary_context_data\character_personality_data\constant_id_3"  # Replace with your input directory
# output_directory = r".\task_1\temporary_context_data\validated_character_personality_data\constant_id_3" # Replace with your output directory
# os.makedirs(output_directory, exist_ok=True)

# threshold = 0.75  # Similarity threshold

# process_json_files(input_directory, output_directory, sentence_transformer_model, threshold)
# print("Processing complete.")
    
