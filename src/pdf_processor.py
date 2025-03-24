import os
import PyPDF2
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from .openai_api import transcribe_image

def extract_pages_as_images(pdf_path):
    """Extract each page of a PDF as an image"""
    images = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        print(f"Extracting {num_pages} pages from PDF...")
        
        for page_num in range(num_pages):
            # This is a placeholder - PyPDF2 doesn't directly convert to images
            # In a real implementation, you would use a library like pdf2image
            # But for simplicity, we're using a workaround here
            page = pdf_reader.pages[page_num]
            # Create a bytes buffer for the PDF page
            buffer = io.BytesIO()
            # Create a new PDF with just this page
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            writer.write(buffer)
            buffer.seek(0)
            
            # Add buffer to images list
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
        # In a real implementation, we would convert the PDF page to an image here
        # For this example, we're passing the PDF buffer directly to the API function
        transcription = transcribe_image(buffer, page_num)
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