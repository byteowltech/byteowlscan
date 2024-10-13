import logging
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
import pytesseract
from PIL import Image
import byteowlscan.utilities.semantic_splitter as SemanticSplitter

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using multiple approaches.
    Attempts text extraction using PDFMiner first, falls back to OCR if necessary.
    
    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    try:
        # Attempt to extract text using PDFMiner
        text = extract_text(pdf_path)
        
        if text and text.strip():
            logger.info("Extracted text using PDFMiner.")
        else:
            # If PDFMiner fails, use OCR as a fallback
            logger.info("PDFMiner extraction failed, attempting OCR.")
            text = _extract_text_from_pdf_using_ocr(pdf_path)
        
        return text
    except Exception as e:
        logger.error("extract_text_from_pdf: %s", e)
        return f"An error occurred: {str(e)}"


def _extract_text_from_pdf_using_ocr(pdf_path):
    """
    Extract text from a PDF by converting each page to an image and using OCR.
    
    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: Extracted text from the PDF using OCR.
    """
    try:
        # Convert PDF pages to images
        pages = convert_from_path(pdf_path, dpi=300)
        text = ""

        # Extract text from each image using Tesseract OCR
        for page in pages:
            text += pytesseract.image_to_string(page, lang='vie')  # Replace 'vie' with 'eng' for English text
        
        return text
    except Exception as e:
        logger.error("_extract_text_from_pdf_using_ocr: %s", e)
        return f"An error occurred during OCR: {str(e)}"


# Function to extract and clean text from Word file
def extract_text_from_word(docx_path):
    """
    Extract text from a Word document by converting it to HTML and then to markdown.
    
    Args:
        docx_path (str): The path to the Word document.

    Returns:
        str: Extracted and cleaned text from the Word document.
    """
    try:
        # Convert DOCX to HTML without images
        html_content = SemanticSplitter.convert_docx_to_html_without_images(docx_path)

        # Convert HTML to markdown
        markdown_content = SemanticSplitter.convert_html_to_markdown(html_content)
        return markdown_content

    except Exception as e:
        logger.error("extract_text_from_word: %s", e)
        return f"An error occurred: {str(e)}"


# Function to extract text from image (JPEG/PNG) using Tesseract OCR
def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image_path (str): The path to the image file.

    Returns:
        str: Extracted text from the image.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='vie')  # Replace 'vie' with 'eng' for English text
        return text
    except Exception as e:
        logger.error("extract_text_from_image: %s", e)
        return f"An error occurred: {str(e)}"
