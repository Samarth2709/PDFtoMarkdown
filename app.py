from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from src.pdf_processor import process_pdf
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        # Generate a unique filename
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        base_filename = os.path.splitext(filename)[0]
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        
        # Save the PDF file
        file.save(pdf_path)
        
        # Process the PDF file and get the output markdown file path
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_filename}_{unique_id}.md")
        
        # Process the PDF in the background and return a job ID
        try:
            process_pdf(pdf_path, output_path)
            return jsonify({
                'success': True,
                'message': 'PDF processed successfully',
                'output_file': f"/download/{os.path.basename(output_path)}"
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format. Please upload a PDF file.'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

@app.route('/view_markdown/<filename>')
def view_markdown(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)