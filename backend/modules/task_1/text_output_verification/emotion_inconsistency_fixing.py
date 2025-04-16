import os
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Define the fixed emotion list with consistent format (intensity-emotion)
FIXED_EMOTIONS = [
    "mild-joy", "moderate-joy", "strong-joy",
    "mild-trust", "moderate-trust", "strong-trust",
    "mild-fear", "moderate-fear", "strong-fear",
    "mild-surprise", "moderate-surprise", "strong-surprise",
    "mild-sadness", "moderate-sadness", "strong-sadness",
    "mild-disgust", "moderate-disgust", "strong-disgust",
    "mild-anger", "moderate-anger", "strong-anger",
    "mild-anticipation", "moderate-anticipation", "strong-anticipation",
    "mild-love", "moderate-love", "strong-love",
    "mild-submission", "moderate-submission", "strong-submission",
    "mild-awe", "moderate-awe", "strong-awe",
    "mild-disappointment", "moderate-disappointment", "strong-disappointment",
    "mild-remorse", "moderate-remorse", "strong-remorse",
    "mild-contempt", "moderate-contempt", "strong-contempt",
    "mild-aggressiveness", "moderate-aggressiveness", "strong-aggressiveness",
    "mild-optimism", "moderate-optimism", "strong-optimism"
]

# Load the Sentence Transformer model (assuming it's already loaded as per your note)
# model = sentence_transformer_model_loader()

def normalize_emotion(emotion_str, model):
    """
    Normalize an emotion string to the closest fixed emotion
    """
    if not emotion_str or not isinstance(emotion_str, str):
        return "neutral"
    
    # Preprocess the input emotion string
    emotion_str = emotion_str.lower().replace("_", "-").replace(" ", "-")
    
    # Special cases for common typos
    emotion_str = emotion_str.replace("mild-", "mild-").replace("moderate-", "moderate-")
    emotion_str = emotion_str.replace("moderate-", "moderate-").replace("strong-", "strong-")
    
    # If already in correct format, return as is
    if emotion_str in FIXED_EMOTIONS:
        return emotion_str
    
    # Encode the input emotion and all fixed emotions
    input_embedding = model.encode([emotion_str])
    fixed_embeddings = model.encode(FIXED_EMOTIONS)
    
    # Calculate cosine similarities
    similarities = cosine_similarity(input_embedding, fixed_embeddings)[0]
    
    # Get the most similar fixed emotion
    most_similar_idx = np.argmax(similarities)
    most_similar_emotion = FIXED_EMOTIONS[most_similar_idx]
    
    return most_similar_emotion

def process_json_file(file_path, model):
    """
    Process a single JSON file to normalize emotion labels
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        modified = False
        for item in data:
            if 'emotion' in item:
                original_emotion = item['emotion']
                normalized_emotion = normalize_emotion(original_emotion, model)
                
                if original_emotion != normalized_emotion:
                    item['emotion'] = normalized_emotion
                    modified = True
        
        if modified:
            # Save the modified data back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Processed and updated: {file_path}")
        else:
            print(f"No changes needed for: {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def process_directory_fixing_emotion(directory_path, model):
    """
    Process all JSON files in a directory
    """
    if not os.path.isdir(directory_path):
        print(f"Directory not found: {directory_path}")
        return
    
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            process_json_file(file_path, model)

# Example usage:
# model = sentence_transformer_model_loader()  # Use your existing model loader
# process_directory('/path/to/your/json/files', model)