import os
import io
import base64
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def extract_text_gemini(image_path):
    """Extract text using Google Gemini Vision API"""
    try:
        # Debug: Print environment variable info
        print(f"DEBUG: GEMINI_API_KEY exists: {bool(gemini_api_key)}")
        print(f"DEBUG: GEMINI_API_KEY length: {len(gemini_api_key) if gemini_api_key else 0}")
        print(f"DEBUG: All env vars starting with GEMINI: {[k for k in os.environ.keys() if 'GEMINI' in k]}")
        
        if not gemini_api_key:
            return "Gemini API key not configured. Please set GEMINI_API_KEY in your .env file or environment variables"
        
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
    method = request.form.get('method', 'gemini')
    language = request.form.get('language', 'eng')
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Convert image to base64 for display
        with open(filepath, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            image_data_url = f"data:image/{filename.split('.')[-1].lower()};base64,{image_base64}"
        
        # Extract text based on selected method
        if method == 'gemini':
            extracted_text = extract_text_gemini(filepath)
        else:
            extracted_text = "Gemini API only"
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Get language name for display
        language_names = {'eng': 'English', 'jpn': 'Japanese'}
        language_display = language_names.get(language, language)
        
        return render_template('result.html', 
                             text=extracted_text, 
                             method=method.title(),
                             language=language_display,
                             filename=file.filename,
                             image_data=image_data_url)
    else:
        flash('Invalid file type. Please upload an image file.')
        return redirect(request.url)

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API endpoint for text extraction"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    method = request.form.get('method', 'gemini')
    language = request.form.get('language', 'eng')
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        if method == 'gemini':
            text = extract_text_gemini(filepath)
        else:
            text = "Gemini API only"
        
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