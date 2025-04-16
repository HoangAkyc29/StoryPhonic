import string
from sentence_transformers import SentenceTransformer, util

def preprocess(text):
    """
    Chuẩn hóa chuỗi: Loại bỏ khoảng trắng, chuyển thành chữ thường và bỏ dấu câu.
    """
    text = text.strip().lower()
    text = text.translate(str.maketrans("", "", string.punctuation))  # Xóa dấu câu
    return text

def compare_and_match(X, A, B, model):
    """
    So sánh X với A và B, trả về kết quả phù hợp theo thứ tự ưu tiên.
    """
    original_X = X.strip()  # Giữ giá trị gốc để trả về
    processed_X = preprocess(X)

    A_processed = {preprocess(a): a.strip() for a in A}  # Mapping giữ nguyên bản gốc
    B_processed = {preprocess(b): b.strip() for b in B}

    # 1. Kiểm tra khớp chính xác trong A
    if processed_X in A_processed:
        return ("1", original_X)

    # 2. Kiểm tra khớp chính xác trong B
    if processed_X in B_processed:
        return ("2", original_X)

    # 3. Tìm kiếm ngữ nghĩa với ngưỡng
    return semantic_similarity_search(original_X, processed_X, B_processed, model)

def semantic_similarity_search(original_X, processed_X, B_processed, model):
    """
    Tìm phần tử có độ tương đồng cao nhất với X trong B. Nếu không có phần tử nào đạt ngưỡng, trả về ("4", None).
    """
    B_keys = list(B_processed.keys())  # Lấy danh sách các bản đã xử lý của B
    embeddings_X = model.encode(processed_X, convert_to_tensor=True)
    embeddings_B = model.encode(B_keys, convert_to_tensor=True)

    # Tính toán độ tương đồng cosine
    cosine_scores = util.cos_sim(embeddings_X, embeddings_B)[0]

    # Tìm giá trị cao nhất
    best_match_index = int(cosine_scores.argmax())
    best_score = float(cosine_scores[best_match_index])  # Chuyển thành float để so sánh

    # Kiểm tra ngưỡng 0.65
    if best_score < 0.65:
        return ("4", original_X)

    best_match = B_processed[B_keys[best_match_index]]  # Lấy giá trị gốc tương ứng

    return ("3", best_match)