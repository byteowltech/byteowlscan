import datetime
import json
import logging
import os
import re
import unicodedata
from pathlib import Path

import byteowlscan.utilities.semantic_splitter as SemanticSplitter
from colorama import Fore
from byteowlscan.models import extract_model
from byteowlscan.utilities.app_config import AppConfig

# Set up logging configuration
logger = logging.getLogger(__name__)

# Save JSON to file
def save_to_json(final_data, file_path, args):
    """
    Saves the combined structured data as a JSON file.

    Args:
        final_data (dict): Extracted data to save.
        file_path (str): Original file path of the resume.
        args: Command line arguments.
    """
    # Get current timestamp for unique file naming
    time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Get file name and clean it
    file_name = clean_filename(get_file_name(file_path))

    # Generate JSON file path
    json_file_path = f"{AppConfig.get('APP_RESULT_FILEPATH')}/{file_name}_{time_stamp}.json"
    if args.outputDir:
        json_file_path = args.outputDir

    # Save data as a JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(final_data, json_file, ensure_ascii=False, indent=4)

    logger.info(f"Processed resume saved as JSON: {json_file_path}")
    print(f"{Fore.RED}Output: {json_file_path}")

# Function to parse the resume and return extracted text
def parse_resume(file_path):
    """
    Parses the resume file and extracts text.

    Args:
        file_path (str): Path to the resume file.

    Returns:
        str: Extracted text from the resume.

    Raises:
        ValueError: If the file type is unsupported.
    """
    logger.info('PARSING RESUME... - File: %s', file_path)

    # Determine file type and call the appropriate extraction method
    if file_path.endswith('.pdf'):
        return extract_model.extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_model.extract_text_from_word(file_path)
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        return extract_model.extract_text_from_image(file_path)
    else:
        logger.error("Unsupported file type!")
        raise ValueError("Unsupported file type")

# Function to check if a dictionary has all values as None or empty
def is_empty_or_null(obj):
    """
    Checks if a dictionary or list has all values as None or empty.

    Args:
        obj: The object to check (can be dict, list, or other).

    Returns:
        bool: True if all values are None or empty, otherwise False.
    """
    if isinstance(obj, dict):
        return all(is_empty_or_null(v) for v in obj.values())
    if isinstance(obj, list):
        return all(is_empty_or_null(v) for v in obj)
    return obj is None or obj == ""

# Function to merge JSON data from chunks, filtering out null/empty data
def merge_json_data(final_data, chunk_data):
    """
    Merges JSON data from chunks, filtering out null/empty values.

    Args:
        final_data (dict): Existing combined data.
        chunk_data (dict): New chunk data to merge.

    Returns:
        dict: Merged data.
    """
    if not isinstance(chunk_data, dict):
        logger.warning(f"Warning: Skipping invalid chunk data: {chunk_data}")
        return final_data

    for key, value in chunk_data.items():
        if is_empty_or_null(value):
            continue

        if key in final_data:
            # Handle merging lists
            if isinstance(final_data[key], list) and isinstance(value, list):
                final_data[key].extend([v for v in value if not is_empty_or_null(v)])
            # Handle merging dictionaries
            elif isinstance(final_data[key], dict) and isinstance(value, dict):
                final_data[key] = merge_json_data(final_data[key], value)
            # Handle merging simple values
            else:
                if final_data[key] != value:
                    final_data[key] = [final_data[key], value] if not isinstance(final_data[key], list) else final_data[key] + [value]
        else:
            final_data[key] = value

    return final_data

# Function to process text into chunks to avoid exceeding token limits
def process_text_in_chunks(file_path, content, chunk_size=16384):
    """
    Processes text content into chunks to avoid exceeding token limits.

    Args:
        file_path (str): Path to the file being processed.
        content (str): Text content to split.
        chunk_size (int): Maximum size of each chunk.

    Returns:
        list: List of text chunks.
    """
    if file_path.endswith(('.pdf', '.docx', '.png', '.jpg', '.jpeg')):
        return SemanticSplitter.splitChunkMarkdown(content, chunk_size) if file_path.endswith(('.docx', '.png', '.jpg', '.jpeg')) else SemanticSplitter.splitChunkText(content, chunk_size)
    return []

# Get all file paths in directory
def get_all_file_paths(directory):
    """
    Gets all file paths in a directory.

    Args:
        directory (str): Path to the directory.

    Returns:
        list: List of file paths.
    """
    return [str(file) for file in Path(directory).rglob('*') if file.is_file()]

# Get file name from path
def get_file_name(file_path):
    """
    Extracts the file name from a given path.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: File name without extension.
    """
    return os.path.splitext(os.path.basename(file_path))[0]

# Clean file name
def clean_filename(filename):
    """
    Cleans the file name by removing diacritics, spaces, and special characters.

    Args:
        filename (str): Original file name.

    Returns:
        str: Cleaned file name.
    """
    # Normalize the filename to decompose Vietnamese characters
    normalized = unicodedata.normalize('NFKD', filename)
    # Remove diacritics by filtering out non-ASCII characters
    no_diacritics = ''.join([c for c in normalized if not unicodedata.combining(c)])
    # Replace spaces with underscores and remove punctuation
    return re.sub(r'[^\w_]', '', no_diacritics.replace(' ', '_'))
