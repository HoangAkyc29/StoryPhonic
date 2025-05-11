import io
import os
import re
import datetime
import shutil  # Import module shutil
import fitz  # PyMuPDF
import PyPDF2

def remove_urls(text):
    """Removes URLs from a string."""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub('', text)

def chunk_text(input_data):
    """
    Chunks a large text data (from string, text file, or PDF file) into smaller chunks.

    Args:
        input_data: A string containing the text, a path to a text file, or a path to a PDF file.

    Returns:
        A list of strings, where each string is a chunk of the input text.
    """
    # input_id = "constant_id_4" #ID này sau sẽ được thay thế để tương ứng với ID của input data này trong SQL

    text = ""

    # 1. Data Loading and PDF Extraction (if applicable)
    if isinstance(input_data, str):
        if os.path.isfile(input_data):  # Assume it's a file path
            try:
                if input_data.lower().endswith(".pdf"):
                    text = extract_text_from_pdf(input_data)
                else:
                    with open(input_data, "r", encoding="utf-8") as f:
                        text = f.read()
            except Exception as e:
                print(f"Error loading file: {e}")
                return []  # Or raise the exception if appropriate
        else:
            text = input_data  # It's directly the text string
    else:
        print("Invalid input data type.  Must be string or file path.")
        return [], 0, None

    # 2. Text Cleaning (optional, but often helpful)
    text = text.strip()  # Remove leading/trailing whitespace
    text = remove_urls(text)

    # 3. Chunking
    chunks = []
    current_chunk = ""
    words = text.split()
    word_count = 0

    for word in words:
        if word_count + 1 <= 400:  # Check word count *before* adding the word
            current_chunk += word + " "  # Add word and space
            word_count += 1
        else:
            # Chunk is full.  Try to find a good split point before adding the word.
            split_point = find_best_split_point(current_chunk)  # Find a split point
            if split_point:
                chunks.append(current_chunk[:split_point].strip())  # Add the chunk
                current_chunk = current_chunk[split_point:].strip() + " " + word + " " # Start a new chunk with the remainder and the current word.
                word_count = len((current_chunk).split())  # Reset word count with new chunk
            else:
                #No split point, just add the whole thing.
                chunks.append(current_chunk.strip())
                current_chunk = word + " "
                word_count = 1 # Reset the count for the new chunk


    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    # print(len(chunks))
    return chunks, len(chunks), text

def save_text_chunk(input_data, input_id, save_folder= None):
    """
    Lưu các đoạn text của chunks vào các file .txt theo thứ tự,
    trong một thư mục con được đặt tên theo input_id.

    Args:
        input_data (str): Đường dẫn tới file PDF hoặc dữ liệu đầu vào khác.
        save_folder (str): Đường dẫn tương đối đến thư mục lưu.

    Returns:
        list: Danh sách đường dẫn tới tất cả các file đã được lưu,
              hoặc None nếu có lỗi xảy ra.
    """
    try:
        chunks, len_chunk, grand_text = chunk_text(input_data)

        # Tạo đường dẫn thư mục con
        pdf_folder_path = os.path.join(save_folder, input_id)

        # Tạo thư mục con nếu chưa tồn tại, nếu tồn tại thì xóa hết nội dung bên trong
        if os.path.exists(pdf_folder_path):
            try:
                shutil.rmtree(pdf_folder_path)  # Xóa thư mục và tất cả nội dung bên trong
                print(f"Đã xóa thư mục cũ và nội dung: {pdf_folder_path}")
            except OSError as e:
                print(f"Lỗi khi xóa thư mục: {pdf_folder_path} - {e}")
                return None  # Trả về None nếu không thể xóa thư mục

        os.makedirs(pdf_folder_path)  # Tạo lại thư mục (dù nó đã tồn tại hoặc vừa bị xóa)

        files_paths = []  # Danh sách để lưu đường dẫn các file đã tạo

        # Lưu các đoạn text vào các file .txt
        for i, chunk in enumerate(chunks):
            file_name = f"{input_id}_{i}.txt"
            file_path = os.path.join(pdf_folder_path, file_name)
            file_path = os.path.abspath(file_path) # Chuyển thành đường dẫn tuyệt đối

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(chunk)
                print(f"Đã lưu chunk {i} vào {file_path}")
                files_paths.append(file_path)  # Thêm đường dẫn file vào danh sách

            except Exception as e:
                print(f"Lỗi khi lưu chunk {i} vào {file_path}: {e}")
                return None  # Trả về None nếu có lỗi khi lưu

        return (files_paths, grand_text)  # Trả về danh sách đường dẫn file nếu thành công

    except Exception as e:
        print(f"Lỗi tổng quan trong save_text_chunk: {e}")
        return None, input_id # Trả về None nếu có bất kỳ lỗi nào xảy ra

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using two methods (PyMuPDF and PyPDF2) as fallback.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A string containing the extracted text.
    """
    text = ""

    # Method 1: PyMuPDF (Generally more accurate)
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"PyMuPDF failed: {e}.  Falling back to PyPDF2.")

    # Method 2: PyPDF2 (Fallback in case PyPDF2 fails)
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"PyPDF2 also failed: {e}")
        return ""


def find_best_split_point(text):
    """
    Finds the best split point in a text chunk based on sentence-ending punctuation.

    Args:
        text: The text chunk to split.

    Returns:
        The index of the best split point in the text, or None if no suitable split point is found.
    """
    # Regex to match sentence-ending punctuation (including quotes and multiple punctuation marks)
    # Includes common abbreviations to prevent splitting there.
    split_regex = r"[.?!;\"']+(?:\s|$|\n)|(?:\s|$|\n)(?:e\.g\.|i\.e\.|etc\.|vs\.)"  #Added some abbreviations

    matches = list(re.finditer(split_regex, text))

    if not matches:
        return None

    # Find the split point closest to the end of the text (but not at the very end)
    best_split_point = None
    for match in reversed(matches):
        if match.end() < len(text):  #Avoid cutting the last character
            best_split_point = match.end()
            break #Use first good match from the end

    return best_split_point

# chunk_text(r"D:\extract_novel_character_data_llama_8B\cote_4.pdf")
# print(save_text_chunk(r"D:\extract_novel_character_data_llama_8B\cote_4.pdf"))