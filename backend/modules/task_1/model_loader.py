from unsloth import FastLanguageModel
from sentence_transformers import SentenceTransformer
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Đường dẫn đến thư mục chứa model (đặt trong task_1/ai_models/sentence_transformer)
SentenceTransformer_MODEL_DIR = os.path.join(os.path.dirname(__file__), "ai_models", "sentence_transformer")
SentenceTransformer_MODEL_NAME = "all-MiniLM-L6-v2"

Llama8BFinetune_MODEL_DIR = os.path.join(os.path.dirname(__file__), "ai_models", "llama_8B_finetune")
Llama8BFinetune_MODEL_NAME = "Cykka/auto_detect_dialogue_character_llama_8B" # Sửa lại cho đúng tên model gốc
LOCAL_LLAMA_MODEL_DIR = os.path.join(Llama8BFinetune_MODEL_DIR, "local_llama_model")  # Thư mục con để lưu bản sao cục bộ

_sentence_transformer_model = None

# Load model sentence_transformer từ thư mục chỉ định (tự động tải nếu chưa có)
def sentence_transformer_model_loader():
    global _sentence_transformer_model
    if _sentence_transformer_model is None:
        _sentence_transformer_model = SentenceTransformer(SentenceTransformer_MODEL_NAME, cache_folder=SentenceTransformer_MODEL_DIR)
        print(f"Model has been loaded into: {SentenceTransformer_MODEL_DIR}")
    return _sentence_transformer_model

# sentence_transformer_model_loader()

_llama_model = None  # Biến private để lưu trữ model
_llama_tokenizer = None # Biến private để lưu trữ tokenizer

def llama_8B_finetune_model_loader():
    """
    Loads the Llama 8B fine-tuned model, downloading it locally if necessary.
    Uses Unsloth's FastLanguageModel.
    """
    global _llama_model, _llama_tokenizer
    if _llama_model is None or _llama_tokenizer is None:
        _llama_model, _llama_tokenizer = FastLanguageModel.from_pretrained(
        model_name = Llama8BFinetune_MODEL_NAME,
        max_seq_length = 32000,
        device_map="auto"
    # token = "hf_...", # use one if using gated models like meta-llama/Llama-2-7b-hf
        )
    return _llama_model, _llama_tokenizer

# llama_8B_finetune_model_loader()

