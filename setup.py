# setup.py
from setuptools import find_packages, setup

setup(
    name="byteowlscan",
    version="0.1.0",
    description="ByteOwlScan is a Python Package designed to extract structed information from a PDF, DOCX, IMAGE Curriculumn Vitae (CVs)/Resume documents. It leverages OCR technology and utilizes the capabilities of ChatGPT AI language model (GPT-3.5 and GPT-4o-mini) to extract pieces of information from the CV content and organize them in a structured JSON-friendly format.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ByteOwlTech",
    author_email="byteowltech@gmail.com",
    url="https://byteowl.tech",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["pyyaml"],  # Add dependencies here if any
)
