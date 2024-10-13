import argparse


def initArgs():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process command-line arguments.")

    # Add an argument
    parser.add_argument('--filePath', type=str, help='Path to file want to scan', required=False, )
    parser.add_argument('--directoryPath', type=str, help='Directory Path contains files want to scan', required=False)
    parser.add_argument('--outputDir', type=str, help='Output directory path', required=False)
    parser.add_argument('--apiKey', type=str, help='Your OPENAI Api Key', required=False)
    parser.add_argument('--model', type=str, help='Your OPENAI model', default="gpt-4o-mini", required=False)
    parser.add_argument('--maxTokens', type=int, help='Max Tokens request and response of GPT', required=False)
    parser.add_argument('--preprocessWithGPT', type=bool, help='Enable preprocess with GPT', required=False, default=False)
    parser.add_argument('--enableChunk', type=bool, help='Enable process chunk text', required=False, default=False)
    parser.add_argument('--config', type=str, help='File path to config', required=False, default="../../config.yaml")

    return parser.parse_args()
