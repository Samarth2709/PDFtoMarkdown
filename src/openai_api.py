import os
import base64
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

def encode_image(image_buffer):
    """Encode image from buffer to base64"""
    # Convert the image buffer to base64
    return base64.b64encode(image_buffer.getvalue()).decode('utf-8')

def transcribe_image(image_buffer, page_num):
    """Send an image to GPT-4o Vision and get a markdown transcription using direct API calls"""
    try:
        print(f"Transcribing page {page_num}...")
        
        # Encode the image
        base64_image = encode_image(image_buffer)
        
        # Prepare the API request payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at transcribing documents into clean, well-formatted markdown. "
                               "Extract all text from the image and format it properly in markdown. "
                               "Preserve headings, lists, tables, and other structural elements. "
                               "If there are figures or images, describe them briefly in [square brackets]."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"This is page {page_num} of a document. Please transcribe all the text from this image into clean markdown format."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 4000
        }
        
        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        # Check for errors
        if response.status_code != 200:
            error_message = f"API error: {response.status_code} - {response.text}"
            print(error_message)
            return f"*Error: {error_message}*"
        
        # Parse the response
        response_data = response.json()
        
        # Extract and return the transcription
        return response_data["choices"][0]["message"]["content"]
    
    except Exception as e:
        error_message = f"Error calling OpenAI API: {str(e)}"
        print(error_message)
        return f"*Error: {error_message}*"