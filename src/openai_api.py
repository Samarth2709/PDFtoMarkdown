import os
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_buffer):
    """Encode image from buffer to base64"""
    # If the buffer is from a PDF, we should convert it to an image first
    # In a real implementation, you would use pdf2image or another library
    # For simplicity, we're returning the raw buffer encoded in base64
    return base64.b64encode(image_buffer.getvalue()).decode('utf-8')

def transcribe_image(image_buffer, page_num):
    """Send an image to GPT-4o Vision and get a markdown transcription"""
    try:
        print(f"Transcribing page {page_num}...")
        
        # Encode the image
        base64_image = encode_image(image_buffer)
        
        # Call the OpenAI API with GPT-4o Vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
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
            max_tokens=4000
        )
        
        # Extract and return the transcription
        return response.choices[0].message.content
    
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")