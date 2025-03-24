# PDF to Markdown Converter

A web application that converts PDF documents to markdown format using GPT-4o Vision model.

## Features

- Simple and intuitive user interface for PDF uploads
- Processes each page of the PDF in parallel for faster conversion
- Uses GPT-4o Vision to accurately transcribe PDF content to markdown
- Preserves document structure including headings, lists, and tables
- Downloads the result as a single markdown file

## Requirements

- Python 3.7 or higher
- OpenAI API key with access to GPT-4o

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Document_reader
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Copy the `.env.example` file to `.env`
   - Add your OpenAI API key to the `.env` file

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and go to `http://127.0.0.1:5000`

3. Upload a PDF file using the web interface

4. Wait for the processing to complete

5. Download the resulting markdown file

## Technical Notes

- The application extracts each page of the PDF and converts it to an image
- Images are sent to the GPT-4o Vision model in parallel
- The model transcribes each page into clean markdown format
- Results are compiled into a single markdown file for download

## Known Limitations

- Large PDFs may take significant time to process
- API costs can accumulate with large documents (each page requires a separate API call)
- You'll need Poppler installed for the pdf2image library to work:
  - On macOS: `brew install poppler`
  - On Ubuntu/Debian: `apt-get install poppler-utils`
  - On Windows: Download and install from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)

## License

MIT