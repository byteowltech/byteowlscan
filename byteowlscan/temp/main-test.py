import argparse
import logging
import os
from typing import Dict, List

import yaml

from byteowlscan.models import extract_gpt
from byteowlscan.utilities import (AppConfig, app_prompt, app_utilities,
                                   initArgs)

logger = logging.getLogger(__name__)

def setup_logging(config_file: str = 'logging_config.yaml') -> None:
    """Setup logging configuration.

    Args:
        config_file (str): Path to the logging configuration file.
    """
    with open(config_file, 'r') as file:
        log_config = yaml.safe_load(file)
    
    log_level = log_config.get('log_level', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_config.get('log_format', "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        handlers=[
            logging.FileHandler(log_config.get('log_file', 'app.log')),
            logging.StreamHandler()
        ]
    )

def preprocessing_with_gpt(extracted_text: str) -> str:
    """Preprocess text with GPT.

    Args:
        extracted_text (str): The text extracted from the resume.

    Returns:
        str: The preprocessed text.
    """
    preprocessing_prompt = app_prompt.generatePreProcessPrompt(extracted_text)
    response = openai.ChatCompletion.create(
        model=AppConfig.get("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": AppConfig.get("OPENAI_PREPROCESS_SYSTEM_CONTENT_PROMPT")},
            {"role": "user", "content": preprocessing_prompt}
        ],
        max_tokens=AppConfig.get("OPENAI_MAX_TOKENS"),
        temperature=AppConfig.get("OPENAI_TEMPERATURE"),
    )
    return response['choices'][0]['message']['content']

def process_resume(args: argparse.Namespace) -> Dict:
    """Process resumes with GPT and save the extracted information.

    Args:
        args (argparse.Namespace): Command line arguments.

    Returns:
        dict: The final extracted information from all resumes.
    """
    files_to_process: List[str] = get_files_list(args)
    final_data: Dict = {}

    logger.info("--- Start scanning resumes ---")
    logger.info("---- Executing ViScanCV Pipeline ----")
    progress_bar = tqdm(files_to_process, desc="Processing files", unit="file", colour="green")

    for resume_path in progress_bar:
        logger.info("Processing resume: %s", resume_path)
        extracted_text: str = app_utilities.parse_resume(resume_path)
        processed_text: str = preprocess_resume_text(extracted_text, args.preprocessWithGPT)
        final_data = extract_information_from_resume(processed_text, args, final_data, resume_path)

    logger.info("Process Completed!")
    return final_data

def get_files_list(args: argparse.Namespace) -> List[str]:
    """Get the list of files to be processed.

    Args:
        args (argparse.Namespace): Command line arguments.

    Returns:
        list: List of file paths to be processed.
    """
    if args.directoryPath:
        return app_utilities.get_all_file_paths(args.directoryPath)
    elif args.filePath:
        return [args.filePath]
    return []

def preprocess_resume_text(extracted_text: str, preprocess_with_gpt: bool) -> str:
    """Preprocess resume text if required.

    Args:
        extracted_text (str): The text extracted from the resume.
        preprocess_with_gpt (bool): Whether to preprocess the text with GPT.

    Returns:
        str: The preprocessed text.
    """
    if preprocess_with_gpt:
        logger.info("Preprocessing text with GPT...")
        return preprocessing_with_gpt(extracted_text)
    return extracted_text

def extract_information_from_resume(extracted_text: str, args: argparse.Namespace, final_data: Dict, resume_path: str) -> Dict:
    """Extract information from resume text.

    Args:
        extracted_text (str): The text extracted from the resume.
        args (argparse.Namespace): Command line arguments.
        final_data (dict): The accumulated extracted data from previous resumes.
        resume_path (str): The path to the current resume being processed.

    Returns:
        dict: The updated extracted information.
    """
    if args.enableChunk:
        text_chunks: List[str] = app_utilities.process_text_in_chunks(resume_path, extracted_text)
        for i, chunk in enumerate(text_chunks):
            logger.info("Processing chunk %d/%d...", i + 1, len(text_chunks))
            chunk_data: Dict = app_utilities.extract_information_with_gpt(chunk)
            final_data = app_utilities.merge_json_data(final_data, chunk_data)
    else:
        logger.info("Extracting information with GPT...")
        final_data = extract_gpt.extract_information_with_gpt(extracted_text, args)
    
    app_utilities.save_to_json(final_data, resume_path, args)
    logger.info("Resume processed successfully: %s", resume_path)
    return final_data

def run_process(args: argparse.Namespace) -> Dict:
    """Run the resume processing pipeline.

    Args:
        args (argparse.Namespace): Command line arguments.

    Returns:
        dict: The final extracted information from all resumes.
    """
    validate_paths(args)
    return process_resume(args)

def validate_paths(args: argparse.Namespace) -> None:
    """Validate input paths and prompt user if needed.

    Args:
        args (argparse.Namespace): Command line arguments.
    """
    if not args.directoryPath and not args.filePath:
        args.filePath = input("Enter the file path (PDF, DOCX, or Image): ")

    if args.outputDir and not os.path.exists(args.outputDir):
        os.mkdir(args.outputDir)

def run(args: argparse.Namespace = None) -> None:
    """Main function to run the resume scanning script.

    Args:
        args (argparse.Namespace, optional): Command line arguments. If None, parse arguments from command line.
    """
    setup_logging()
    if args is None:
        args = initArgs()
    
    file_config: str = args.config if args and args.config else "../config.yaml"
    AppConfig.init_config(file_config)
    openai.api_key = AppConfig.get("OPENAI_API_KEY")

    structured_data: Dict = run_process(args)
    if structured_data:
        logger.info("Information extracted and structured data saved successfully.")
    else:
        logger.error("Failed to extract information from the resume.")

__all__ = ['run']

if __name__ == "__main__":
    run()
