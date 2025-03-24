import os
import PyPDF2
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from pdf2image import convert_from_path
from src.openai_api import transcribe_image

def extract_pages_as_images(pdf_path):
    """Extract each page of a PDF as an image"""
    images = []
    
    try:
        # Get the number of pages
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
        
        print(f"Extracting {num_pages} pages from PDF...")
        
        # Convert PDF pages to images using pdf2image
        pdf_images = convert_from_path(pdf_path, dpi=200)
        
        for page_num, img in enumerate(pdf_images):
            # Create a buffer for each image
            buffer = io.BytesIO()
            # Save the image to the buffer in JPEG format
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            
            # Add buffer to images list
            images.append({
                'page_num': page_num + 1,
                'buffer': buffer
            })
    except Exception as e:
        print(f"Error extracting pages: {str(e)}")
        # Fallback to the old method if pdf2image fails
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"Falling back to PyPDF2 for {num_pages} pages...")
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                buffer = io.BytesIO()
                writer = PyPDF2.PdfWriter()
                writer.add_page(page)
                writer.write(buffer)
                buffer.seek(0)
                
                images.append({
                    'page_num': page_num + 1,
                    'buffer': buffer
                })
            
    return images

def process_single_page(page_data):
    """Process a single page and get its transcription"""
    page_num = page_data['page_num']
    buffer = page_data['buffer']
    
    try:
        # Send the image buffer to the OpenAI API for transcription
        transcription = transcribe_image(buffer, page_num)
        
        # Check if the transcription contains an error message
        if transcription.startswith("*Error:"):
            print(f"Error transcribing page {page_num}")
            return {
                'page_num': page_num,
                'content': transcription
            }
            
        return {
            'page_num': page_num,
            'content': transcription
        }
    except Exception as e:
        print(f"Error processing page {page_num}: {str(e)}")
        return {
            'page_num': page_num,
            'content': f"*Error transcribing page {page_num}: {str(e)}*"
        }

def process_pdf(pdf_path, output_path):
    """Process the PDF and generate a markdown file"""
    # Extract pages as images
    page_images = extract_pages_as_images(pdf_path)
    total_pages = len(page_images)
    
    print(f"Processing {total_pages} pages in parallel...")
    
    # Process pages in parallel
    results = []
    with ThreadPoolExecutor(max_workers=min(10, total_pages)) as executor:
        # Map the process_single_page function to each page image
        futures = list(tqdm(
            executor.map(process_single_page, page_images),
            total=total_pages,
            desc="Transcribing pages"
        ))
        
        # Collect results
        for result in futures:
            results.append(result)
    
    # Sort results by page number
    results.sort(key=lambda x: x['page_num'])
    
    # Combine the transcriptions into a single markdown file
    with open(output_path, 'w', encoding='utf-8') as md_file:
        for result in results:
            md_file.write(f"## Page {result['page_num']}\n\n")
            md_file.write(f"{result['content']}\n\n")
            md_file.write("---\n\n")
    
    print(f"PDF processing complete. Output saved to {output_path}")
    return output_path