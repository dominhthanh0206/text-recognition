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
    """Extract text using Google Gemini Vision API with comprehensive structured field extraction"""
    try:
        # Debug: Print environment variable info
        print(f"DEBUG: GEMINI_API_KEY exists: {bool(gemini_api_key)}")
        print(f"DEBUG: GEMINI_API_KEY length: {len(gemini_api_key) if gemini_api_key else 0}")
        print(f"DEBUG: All env vars starting with GEMINI: {[k for k in os.environ.keys() if 'GEMINI' in k]}")
        
        if not gemini_api_key:
            return {
                "text": "Gemini API key not configured. Please set GEMINI_API_KEY in your .env file or environment variables",
                "personal_info": {
                    "name": "",
                    "phone": "",
                    "email": "",
                    "date_of_birth": "",
                    "other_personal": ""
                },
                "transactional_info": {
                    "invoice_number": "",
                    "order_id": "",
                    "total_amount": "",
                    "payment_method": "",
                    "other_transactional": ""
                },
                "dates": {
                    "due_date": "",
                    "issue_date": "",
                    "other_dates": ""
                },
                "locations": {
                    "addresses": "",
                    "other_locations": ""
                },
                "other_data": ""
            }
        
        # Load and prepare image
        image = Image.open(image_path)
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate text extraction with comprehensive structured field detection
        response = model.generate_content([
            """Extract ALL text from this image and classify key pieces of information into structured categories.

        IMPORTANT: Return ONLY valid JSON format, no markdown, no explanations, no code blocks.

        Response format:
        {
            "text": "Complete extracted text here - preserve exact formatting",
            "personal_info": {
                "name": "extracted full name if found, empty string if not",
                "phone": "extracted phone number if found, empty string if not",
                "email": "extracted email address if found, empty string if not",
                "date_of_birth": "extracted date of birth if found, empty string if not",
                "other_personal": "any other personal information (ID numbers, titles, etc.)"
            },
            "transactional_info": {
                "invoice_number": "extracted invoice/receipt number if found, empty string if not",
                "order_id": "extracted order ID or reference number if found, empty string if not",
                "total_amount": "extracted total amount/price if found, empty string if not",
                "payment_method": "extracted payment method if found, empty string if not",
                "other_transactional": "any other transaction-related info (taxes, discounts, etc.)"
            },
            "dates": {
                "due_date": "extracted due date if found, empty string if not",
                "issue_date": "extracted issue/created date if found, empty string if not",
                "other_dates": "any other important dates found"
            },
            "locations": {
                "addresses": "extracted addresses if found, empty string if not",
                "other_locations": "any other location information (cities, countries, etc.)"
            },
            "other_data": "any other structured or identifiable data not covered above"
        }

        Requirements:
        - Read every word precisely, including Vietnamese and Japanese text with proper diacritics
        - Preserve the original formatting and line breaks in the "text" field
        - Carefully classify information into appropriate categories
        - For personal info: Look for names, phone numbers, emails, dates of birth, ID numbers, titles
        - For transactional info: Look for invoice numbers, order IDs, amounts, currencies, payment methods, taxes
        - For dates: Look for due dates, issue dates, expiry dates, etc. in various formats
        - For locations: Look for complete addresses, postal codes, cities, countries, regions
        - If multiple instances found, include all separated by commas
        - Use empty strings for missing fields
        - Return ONLY the JSON object, no other text

        Extract and classify all information exactly as it appears in the image.""",
            image
        ])
        
        # Try to parse JSON response
        try:
            import json
            # Clean the response text - remove markdown code blocks if present
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            result = json.loads(response_text)
            
            # Ensure result is a dictionary and has expected structure
            if isinstance(result, dict) and 'text' in result:
                return result
            else:
                # If not proper structure, create one with the response as text
                return {
                    "text": response.text,
                    "personal_info": {
                        "name": "",
                        "phone": "",
                        "email": "",
                        "date_of_birth": "",
                        "other_personal": ""
                    },
                    "transactional_info": {
                        "invoice_number": "",
                        "order_id": "",
                        "total_amount": "",
                        "payment_method": "",
                        "other_transactional": ""
                    },
                    "dates": {
                        "due_date": "",
                        "issue_date": "",
                        "other_dates": ""
                    },
                    "locations": {
                        "addresses": "",
                        "other_locations": ""
                    },
                    "other_data": ""
                }
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            print(f"DEBUG: Raw response: {response.text[:500]}...")
            # Fallback if response is not valid JSON
            return {
                "text": response.text,
                "personal_info": {
                    "name": "",
                    "phone": "",
                    "email": "",
                    "date_of_birth": "",
                    "other_personal": ""
                },
                "transactional_info": {
                    "invoice_number": "",
                    "order_id": "",
                    "total_amount": "",
                    "payment_method": "",
                    "other_transactional": ""
                },
                "dates": {
                    "due_date": "",
                    "issue_date": "",
                    "other_dates": ""
                },
                "locations": {
                    "addresses": "",
                    "other_locations": ""
                },
                "other_data": ""
            }
    except Exception as e:
        return {
            "text": f"Error with Gemini Vision API: {str(e)}",
            "personal_info": {
                "name": "",
                "phone": "",
                "email": "",
                "date_of_birth": "",
                "other_personal": ""
            },
            "transactional_info": {
                "invoice_number": "",
                "order_id": "",
                "total_amount": "",
                "payment_method": "",
                "other_transactional": ""
            },
            "dates": {
                "due_date": "",
                "issue_date": "",
                "other_dates": ""
            },
            "locations": {
                "addresses": "",
                "other_locations": ""
            },
            "other_data": ""
        }

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
            extraction_result = extract_text_gemini(filepath)
        else:
            extraction_result = {
                "text": "Gemini API only",
                "personal_info": {
                    "name": "",
                    "phone": "",
                    "email": "",
                    "date_of_birth": "",
                    "other_personal": ""
                },
                "transactional_info": {
                    "invoice_number": "",
                    "order_id": "",
                    "total_amount": "",
                    "payment_method": "",
                    "other_transactional": ""
                },
                "dates": {
                    "due_date": "",
                    "issue_date": "",
                    "other_dates": ""
                },
                "locations": {
                    "addresses": "",
                    "other_locations": ""
                },
                "other_data": ""
            }
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Get language name for display
        language_names = {'eng': 'English', 'jpn': 'Japanese'}
        language_display = language_names.get(language, language)
        
        return render_template('result.html', 
                             text=extraction_result.get('text', ''),
                             personal_info=extraction_result.get('personal_info', {}),
                             transactional_info=extraction_result.get('transactional_info', {}),
                             dates=extraction_result.get('dates', {}),
                             locations=extraction_result.get('locations', {}),
                             other_data=extraction_result.get('other_data', ''),
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
            extraction_result = extract_text_gemini(filepath)
        else:
            extraction_result = {
                "text": "Gemini API only",
                "personal_info": {
                    "name": "",
                    "phone": "",
                    "email": "",
                    "date_of_birth": "",
                    "other_personal": ""
                },
                "transactional_info": {
                    "invoice_number": "",
                    "order_id": "",
                    "total_amount": "",
                    "payment_method": "",
                    "other_transactional": ""
                },
                "dates": {
                    "due_date": "",
                    "issue_date": "",
                    "other_dates": ""
                },
                "locations": {
                    "addresses": "",
                    "other_locations": ""
                },
                "other_data": ""
            }
        
        os.remove(filepath)
        
        return jsonify({
            'text': extraction_result.get('text', ''),
            'personal_info': extraction_result.get('personal_info', {}),
            'transactional_info': extraction_result.get('transactional_info', {}),
            'dates': extraction_result.get('dates', {}),
            'locations': extraction_result.get('locations', {}),
            'other_data': extraction_result.get('other_data', ''),
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