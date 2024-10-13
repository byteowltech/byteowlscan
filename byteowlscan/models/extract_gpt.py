import json
import logging
import re

import openai
from byteowlscan.utilities import AppConfig, app_prompt

# Set up logging configuration
logger = logging.getLogger(__name__)

# Function to interact with ChatGPT and extract structured information
def extract_information_with_gpt(text_chunk, args):
    #Set prompt
    prompt = app_prompt.generateExtractInfo(text_chunk)
    openai_model = args.model if args.model else AppConfig.get("OPENAI_MODEL")
    openai_max_tokens = AppConfig.get("OPENAI_MAX_TOKENS")
    
    if args.model == "gpt-4o-mini":
        openai_max_tokens = AppConfig.get("OPENAI_MAX_TOKENS")
    elif args.model == "gpt-3.5-turbo":
        openai_max_tokens = 4096
    else:
        openai_max_tokens = args.maxTokens
        
    #Send request and get response from openai api
    response = openai.ChatCompletion.create(
        model=openai_model,  # You can replace it with any other model you are using
        messages=[
            {"role": "system", "content": AppConfig.get("OPENAI_PREPROCESS_EXTRACT_INFO_PROMPT")},
            {"role": "user", "content": prompt}
        ],
        max_tokens=openai_max_tokens,
        temperature=AppConfig.get("OPENAI_TEMPERATURE")
    )

    # Extract the structured JSON response from GPT
    json_response = response['choices'][0]['message']['content'].strip()
    logger.info('json_response: %s', json_response)

   # Step 1: Use regex to extract the JSON part from the response, ignoring extraneous text
    json_match = re.search(r'\{.*\}', json_response, re.DOTALL)
    if json_match:
        json_string = json_match.group(0)
        try:
            # Try to parse the cleaned JSON string
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print("Error: Could not decode the response into valid JSON:", e)
            logger.error("Error: Could not decode the response into valid JSON:", e)
            return json_response  # Return raw string if decoding fails
    else:
        print("No valid JSON found in response.")
        logger.info("No valid JSON found in response.")
        return json_response  # If no JSON was found, return raw response for debugging
