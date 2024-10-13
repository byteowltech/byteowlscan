import docx
import os
import fitz  # PyMuPDF for PDF
import docx  # For Word files
import pytesseract  # For OCR
from PIL import Image
import json
import openai
import re
import utilities.SemanticSplitter as SemanticSplitter
from PyPDF2 import PdfReader
import spacy
import mammoth
import nltk
import textacy.preprocessing as tp
from spellchecker import SpellChecker

# Set your OpenAI API key
openai.api_key = 'YOUR_OPEN_API_KEY'


def preprocessing_with_gpt(extracted_text):
    # Define the preprocessing prompt
    preprocessing_prompt = f"""
    Preprocess the extracted text from a resume to make it clear and structured without losing any content. Follow these instructions:

    1. Preserve every piece of information exactly as it appears.
    2. Merge sentences that are split by unnecessary line breaks, but maintain breaks between meaningful sections.
    3. Remove redundant spaces and ensure proper punctuation, spacing, and capitalization.
    4. Fix minor formatting issues like missing punctuation or capitalization errors.
    5. Exclude non-content elements such as headers, footers, page numbers, or any irrelevant data.
    6. Do not modify or rephrase the content in any way.
    7. Ensure the text is well-organized and readable while retaining all original details and content structure.

    Here is the extracted text to preprocess:
    \"\"\"{extracted_text}\"\"\"
    """

    # Make the request to OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert at preprocessing unstructured text into clean, structured, and readable content."},
            {"role": "user", "content": preprocessing_prompt}
        ],
        max_tokens=4096,
        temperature=0,
    )

    # Extract the cleaned text from the response
    return response['choices'][0]['message']['content']

# Bộ xử lý mạnh mẽ cho văn bản
def preprocess_resume_text(extracted_text):
    # 1. Loại bỏ các ký tự không cần thiết như header, footer, số trang
    text = re.sub(r'Page \d+ of \d+', '', extracted_text)
    text = re.sub(r'[\r\n]+', '\n', text)  # Loại bỏ các dòng trống liên tiếp
    text = tp.normalize_whitespace(text)   # Chuẩn hóa khoảng trắng
    text = tp.replace_urls(text, "")       # Loại bỏ URL

    # 2. Loại bỏ khoảng trắng thừa và định dạng không cần thiết
    text = re.sub(r'\s+', ' ', text).strip()

    # 3. Chuẩn hóa văn bản bằng spaCy (tách từ, loại bỏ thực thể không cần thiết)
    doc = nlp(text)
    cleaned_text = []
    for ent in doc.ents:
        if ent.label_ not in ["PAGE", "EMAIL"]:  # Loại bỏ các thực thể không cần thiết
            cleaned_text.append(ent.text)
    text = ' '.join(cleaned_text)

    # 4. Loại bỏ các dòng lặp và trùng lặp
    lines = text.split("\n")
    unique_lines = list(set(lines))
    text = "\n".join(unique_lines)

    # 5. Sửa lỗi chính tả bằng pyspellchecker
    spell = SpellChecker()
    corrected_text = []
    for word in text.split():
        corrected_text.append(spell.correction(word))
    text = ' '.join(corrected_text)

    return text


# Function to interact with ChatGPT and extract structured information


def extract_information_with_gpt(text_chunk):
    prompt = """
    Extract all relevant information from the resume text, which may be written in either plain text or Markdown, and return it in a valid JSON format based on the provided schema. Follow these guidelines:

    1. Property names must be in English using camelCase.
    2. Extract all information exactly as it appears in the text, without omissions, rephrasing, adjustments, or translations.
    3. For work experience, extract all job responsibilities, achievements, and details completely.
    4. Exclude Markdown formatting during the extraction.
    5. If a field does not exist in the resume, exclude that field from the JSON (do not append null or empty values).
    6. The JSON must include all available data, organized according to the schema, and be valid for backend systems.
    7. For any content not directly matching the schema, create a new field based on the meaning and structure of the information in the resume.

    Use the following JSON schema as the base for extraction:

    {
        "candidateInformation": { ... },
        "education": [ ... ],
        "trainingCourses": [ ... ],
        "languageSkills": { ... },
        "computerSkills": { ... },
        "workExperience": [ ... ],
        "salary": { ... },
        "references": [ ... ],
        "availability": { ... },
        "expectedSalary": { ... },
        "reasonForApplication": [""],
        "careerPlan": "",
        "familyInformation": [ ... ],
        "commitmentStatement": "",
        "signDate": "",
        "technicalSkills": [ ... ],
        "achievementsAndAwards": [ ... ],
        "projects": [ ... ],
        "volunteerExperience": [ ... ],
        "additionalInformation": {}
    }

    Resume text:
    """ + text_chunk + """
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can replace it with any other model you are using
        messages=[
            {"role": "system", "content": "You are an assistant that extracts structured information from resumes without omitting any information or making creative modifications."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        temperature=0
    )

    # Extract the structured JSON response from GPT
    json_response = response['choices'][0]['message']['content'].strip()
    print('json_response', json_response)

   # Step 1: Use regex to extract the JSON part from the response, ignoring extraneous text
    json_match = re.search(r'\{.*\}', json_response, re.DOTALL)
    if json_match:
        json_string = json_match.group(0)
        try:
            # Try to parse the cleaned JSON string
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print("Error: Could not decode the response into valid JSON:", e)
            return json_response  # Return raw string if decoding fails
    else:
        print("No valid JSON found in response.")
        return json_response  # If no JSON was found, return raw response for debugging

# Function to process text into chunks to avoid exceeding token limits


def process_text_in_chunks(file_path, content, chunk_size=4096):
    chunks = []
    if file_path.endswith('.pdf'):
        chunks = SemanticSplitter.splitChunkText(content, chunk_size)
    elif file_path.endswith('.docx'):
        chunks = SemanticSplitter.splitChunkMarkdown(content, chunk_size)
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        chunks = SemanticSplitter.splitChunkMarkdown(content, chunk_size)

    return chunks

# Replace the previous extract_information function


def process_resume_with_gpt(file_path):
    extracted_text = parse_resume(file_path)

    print('===== 02. EXTRACTED TEXT =====')
    print('extracted_text', extracted_text)
    
    preprocess_text = preprocessing_with_gpt(extracted_text)
    print('preprocess_text', preprocess_text)
    

    # Split the extracted text into smaller chunks
    text_chunks = process_text_in_chunks(file_path, preprocess_text)
    print(text_chunks)

    final_data = {}

    # # Send each chunk to GPT-3.5 for dynamic information extraction
    # for i, chunk in enumerate(text_chunks):
    #     print(f"Processing chunk {i+1}/{len(text_chunks)}...")
    #     chunk_data = extract_information_with_gpt(chunk)
    #     print(f"Chunk data success")
    #     # Merge the result of this chunk into the final data
    #     final_data = merge_json_data(final_data, chunk_data)
    #     print(f"Merge json data => final_data")

    print('==== 03. STRUCTURED DATA =====')
    print('final_data', final_data)

    # Save the combined structured data as a JSON file
    json_file_path = f"/Users/hoangnhh/Sources/NLP/ScanResume/outputs/results.json"
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(final_data, json_file, ensure_ascii=False, indent=4)

    print(f"Processed resume saved as JSON: {json_file_path}")
    return final_data

# Function to extract text from PDF


def extract_text_from_pdf(pdf_path):
    # pdf_document = fitz.open(pdf_path)
    # text = ""
    # for page_num in range(pdf_document.page_count):
    #     page = pdf_document[page_num]
    #     text += page.get_text()
    # return text

    reader = PdfReader(pdf_path)
    page_num = len(reader.pages)
    page = reader.pages

    text = ""

    # Extract text from each page
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()

    # html_content = SemanticSplitter.convert_pdf_to_html(pdf_path)

    # # Convert HTML to markdown
    # markdown_content = SemanticSplitter.convert_html_to_markdown(
    #     html_content)

    return text

# Function to extract and clean text from Word file


def extract_text_from_word(docx_path):
    try:
        html_content = ""
        # Get HTML content
        html_content = SemanticSplitter.convert_docx_to_html_without_images(
            docx_path)

        # Convert HTML to markdown
        markdown_content = SemanticSplitter.convert_html_to_markdown(
            html_content)

        return markdown_content

    except Exception as e:
        return f"An error occurred: {str(e)}"


# Function to extract text from image (JPEG/PNG) using Tesseract OCR


def extract_text_from_image(image_path):
    img = Image.open(image_path)
    # Vietnamese language for Tesseract
    text = pytesseract.image_to_string(img, lang='vie')
    return text

# Function to parse the resume and return extracted text


def parse_resume(file_path):
    print('===== 01. PARSE RESUME =====')
    print('file_path', file_path)

    if file_path.endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        extracted_text = extract_text_from_word(file_path)
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        extracted_text = extract_text_from_image(file_path)
    else:
        raise ValueError("Unsupported file type")

    return extracted_text

# Function to check if a dictionary has all values as None or empty


def is_empty_or_null(obj):
    if isinstance(obj, dict):
        return all(is_empty_or_null(v) for v in obj.values())
    if isinstance(obj, list):
        return all(is_empty_or_null(v) for v in obj)
    return obj is None or obj == ""

# Function to merge JSON data from chunks, filtering out null/empty data


def merge_json_data(final_data, chunk_data):
    if isinstance(chunk_data, dict):
        for key, value in chunk_data.items():
            # Skip if the value is null or empty
            if is_empty_or_null(value):
                continue

            if key in final_data:
                # Handle if the value is a list: append to the existing list after filtering
                if isinstance(final_data[key], list) and isinstance(value, list):
                    final_data[key].extend(
                        [v for v in value if not is_empty_or_null(v)])

                # Handle if the value is a dictionary: recursively update the dictionary
                elif isinstance(final_data[key], dict) and isinstance(value, dict):
                    final_data[key] = merge_json_data(
                        final_data[key], value)  # Recursive merge

                # Handle simple values (strings, integers, etc.): Skip null or empty, merge others
                else:
                    if not is_empty_or_null(value):
                        if final_data[key] != value:
                            final_data[key] = [final_data[key], value] if not isinstance(
                                final_data[key], list) else final_data[key] + [value]
            else:
                # If the key does not exist in final_data and value is not null/empty, add it
                if not is_empty_or_null(value):
                    final_data[key] = value
    else:
        print(f"Warning: Skipping invalid chunk data: {chunk_data}")

    return final_data


# Testing the script by parsing a PDF/Word/Image resume
if __name__ == '__main__':
    file_path = input("Enter the file path (PDF, DOCX, or Image): ")
    if os.path.exists(file_path):
        structured_data = process_resume_with_gpt(file_path)
        print("Information extracted and structured data saved successfully.")
    else:
        print("File not found!")
