import os
import io
import base64
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set TESSDATA_PREFIX environment variable if not set
tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'
if os.path.exists(tessdata_path):
    os.environ['TESSDATA_PREFIX'] = tessdata_path
    # Also try setting pytesseract config
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'jfif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure OpenAI (optional)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure Gemini (optional)
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_tesseract(image_path, language='eng'):
    """Extract text using Tesseract OCR"""
    try:
        # Set TESSDATA_PREFIX for different environments
        if os.name == 'nt':  # Windows
            tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'
            if os.path.exists(tessdata_path):
                os.environ['TESSDATA_PREFIX'] = tessdata_path
        else:  # Linux/Unix (Railway, Docker)
            tessdata_paths = [
                '/usr/share/tesseract-ocr/5/tessdata',
                '/usr/share/tesseract-ocr/4.00/tessdata',
                '/usr/share/tessdata'
            ]
            for path in tessdata_paths:
                if os.path.exists(path):
                    os.environ['TESSDATA_PREFIX'] = path
                    break
        
        # Check if Tesseract is available
        pytesseract.get_tesseract_version()
        
        # Check if the requested language is available
        available_langs = pytesseract.get_languages()
        print(f"Available languages: {available_langs}")
        print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")
        print(f"OS: {os.name}, Platform: {os.uname() if hasattr(os, 'uname') else 'Unknown'}")
        
        # Debug: Check all possible tessdata paths
        possible_paths = [
            '/usr/share/tesseract-ocr/5/tessdata',
            '/usr/share/tesseract-ocr/4.00/tessdata', 
            '/usr/share/tessdata',
            '/usr/local/share/tessdata'
        ]
        for path in possible_paths:
            exists = os.path.exists(path)
            print(f"Path {path}: {'EXISTS' if exists else 'NOT FOUND'}")
            if exists:
                try:
                    files = os.listdir(path)
                    jpn_files = [f for f in files if 'jpn' in f.lower()]
                    print(f"  Japanese files in {path}: {jpn_files}")
                except Exception as e:
                    print(f"  Cannot list {path}: {e}")
        
        if language not in available_langs:
            if language == 'jpn':
                return """❌ Japanese language data not found for Tesseract.

🔧 To install Japanese language support:
1. Download Japanese language data from: https://github.com/tesseract-ocr/tessdata
2. Download 'jpn.traineddata' file
3. Copy it to your Tesseract tessdata folder (usually C:\\Program Files\\Tesseract-OCR\\tessdata\\)
4. Try again

Alternative: Use the OpenAI Vision API option instead."""
            else:
                return f"❌ Language '{language}' is not available.\n\nAvailable languages: {', '.join(available_langs)}"
        
        # Open image and extract text with specified language
        image = Image.open(image_path)
        
        # Try with explicit tessdata path based on environment
        tessdata_prefix = os.environ.get('TESSDATA_PREFIX')
        if tessdata_prefix:
            config = f'--tessdata-dir "{tessdata_prefix}"'
            text = pytesseract.image_to_string(image, lang=language, config=config)
        else:
            # Fallback without explicit config
            text = pytesseract.image_to_string(image, lang=language)
        
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        return """❌ Tesseract OCR is not installed or not in your PATH.

🔧 To install Tesseract on Windows:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer as Administrator
3. Make sure to check "Add Tesseract to PATH" during installation
4. Restart your terminal and try again

Alternative: Use the OpenAI Vision API option instead (requires API key)."""
    except Exception as e:
        error_msg = str(e)
        return f"Error with Tesseract OCR: {error_msg}\n\nTip: Make sure Tesseract is properly installed and the selected language is supported."

def extract_text_openai(image_path):
    """Extract text using OpenAI Vision API"""
    try:
        if not openai.api_key:
            return "OpenAI API key not configured"
        
        # Convert image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. If there's no text, just say 'No text found'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with OpenAI Vision API: {str(e)}"

def extract_text_gemini(image_path):
    """Extract text using Google Gemini Vision API"""
    try:
        if not gemini_api_key:
            return "Gemini API key not configured. Please set GEMINI_API_KEY in your .env file"
        
        # Load and prepare image
        image = Image.open(image_path)
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate text extraction with improved prompt
        response = model.generate_content([
            """Extract ALL text from this image accurately.
            Requirements:
            - Read every word precisely, including Vietnamese text with proper diacritics
            - Preserve the original formatting and structure of the text
            - If there are multiple columns or sections, read them in logical order
            - If no text is found, simply respond 'No text found'
            - Do not add any explanations or comments

            Please extract all text exactly as it appears in the image.""",
            image
        ])
        
        return response.text
    except Exception as e:
        return f"Error with Gemini Vision API: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    method = request.form.get('method', 'tesseract')
    language = request.form.get('language', 'eng')
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text based on selected method
        if method == 'openai':
            extracted_text = extract_text_openai(filepath)
        elif method == 'gemini':
            extracted_text = extract_text_gemini(filepath)
        else:
            extracted_text = extract_text_tesseract(filepath, language)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Get language name for display
        language_names = {'eng': 'English', 'jpn': 'Japanese'}
        language_display = language_names.get(language, language)
        
        return render_template('result.html', 
                             text=extracted_text, 
                             method=method.title(),
                             language=language_display,
                             filename=file.filename)
    else:
        flash('Invalid file type. Please upload an image file.')
        return redirect(request.url)

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API endpoint for text extraction"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    method = request.form.get('method', 'tesseract')
    language = request.form.get('language', 'eng')
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        if method == 'openai':
            text = extract_text_openai(filepath)
        elif method == 'gemini':
            text = extract_text_gemini(filepath)
        else:
            text = extract_text_tesseract(filepath, language)
        
        os.remove(filepath)
        
        return jsonify({
            'text': text,
            'method': method,
            'language': language,
            'filename': file.filename
        })
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 