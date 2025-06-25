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
            """Please extract and classify any key pieces of information found in this image, such as:

        Personal info (name, phone, date of birth, email...)
        Transactional info (invoice numbers, order IDs, total amount, payment method...)
        Dates (due dates, issue dates, etc.)
        Locations or addresses
        Any other structured or identifiable data

        IMPORTANT: Return ONLY valid JSON format, no markdown, no explanations, no code blocks.

        Response format:
        {
            "text": "Complete extracted text here - preserve exact formatting and line breaks",
            "personal_info": {
                "name": "full name if found, empty string if not",
                "phone": "phone number if found, empty string if not",
                "email": "email address if found, empty string if not",
                "date_of_birth": "date of birth if found, empty string if not",
                "other_personal": "ID numbers, titles, social security, employee ID, etc."
            },
            "transactional_info": {
                "invoice_number": "invoice/receipt number if found, empty string if not",
                "order_id": "order ID or reference number if found, empty string if not",
                "total_amount": "total amount/price with currency if found, empty string if not",
                "payment_method": "payment method (cash, card, transfer, etc.) if found, empty string if not",
                "other_transactional": "taxes, discounts, subtotals, item details, etc."
            },
            "dates": {
                "due_date": "due date/deadline if found, empty string if not",
                "issue_date": "issue/created/published date if found, empty string if not",
                "other_dates": "expiry dates, birth dates, event dates, etc."
            },
            "locations": {
                "addresses": "complete addresses with street, city, postal codes if found, empty string if not",
                "other_locations": "cities, countries, regions, building names, etc."
            },
            "other_data": "any other structured or identifiable data not covered above (license numbers, account numbers, company info, etc.)"
        }

        Extraction Guidelines:
        - Read EVERY word precisely, including Vietnamese, Japanese, and all languages with proper diacritics
        - Preserve original formatting and line breaks in the "text" field
        - Look for ALL types of structured information, not just obvious ones
        - For personal info: Names, phones, emails, DOB, IDs, titles, positions
        - For transactional info: Invoice numbers, order IDs, amounts, currencies, payment methods, taxes, discounts
        - For dates: Due dates, issue dates, expiry dates, birth dates, event dates - in ANY format
        - For locations: Complete addresses, postal codes, cities, countries, regions, buildings
        - Include multiple instances separated by commas
        - Use empty strings for fields not found
        - Be thorough - extract even small details that might be important
        - Return ONLY the JSON object, no other text

        Extract and classify ALL information exactly as it appears in the image.""",
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

def format_extracted_info(extraction_result):
    """Format all extracted information into a single readable text"""
    if not isinstance(extraction_result, dict):
        return "No identifiable information found."
    
    formatted_info = []
    
    # Personal Information
    personal_info = extraction_result.get('personal_info', {})
    if personal_info.get('name'):
        formatted_info.append(f"Name: {personal_info['name']}")
    if personal_info.get('phone'):
        formatted_info.append(f"Phone: {personal_info['phone']}")
    if personal_info.get('email'):
        formatted_info.append(f"Email: {personal_info['email']}")
    if personal_info.get('date_of_birth'):
        formatted_info.append(f"Date of Birth: {personal_info['date_of_birth']}")
    if personal_info.get('other_personal'):
        formatted_info.append(f"Other Personal Info: {personal_info['other_personal']}")
    
    # Transactional Information
    transactional_info = extraction_result.get('transactional_info', {})
    trans_items = []
    if transactional_info.get('invoice_number'):
        trans_items.append(f"Invoice: {transactional_info['invoice_number']}")
    if transactional_info.get('order_id'):
        trans_items.append(f"Order ID: {transactional_info['order_id']}")
    if transactional_info.get('total_amount'):
        trans_items.append(f"Total Amount: {transactional_info['total_amount']}")
    if transactional_info.get('payment_method'):
        trans_items.append(f"Payment Method: {transactional_info['payment_method']}")
    if transactional_info.get('other_transactional'):
        trans_items.append(f"Other Transaction Info: {transactional_info['other_transactional']}")
    
    if trans_items:
        formatted_info.append("Transactional Information:")
        for item in trans_items:
            formatted_info.append(f"  - {item}")
    
    # Dates
    dates = extraction_result.get('dates', {})
    date_items = []
    if dates.get('due_date'):
        date_items.append(f"Due Date: {dates['due_date']}")
    if dates.get('issue_date'):
        date_items.append(f"Issue Date: {dates['issue_date']}")
    if dates.get('other_dates'):
        date_items.append(f"Other Dates: {dates['other_dates']}")
    
    if date_items:
        formatted_info.append("Dates:")
        for item in date_items:
            formatted_info.append(f"  - {item}")
    
    # Locations
    locations = extraction_result.get('locations', {})
    if locations.get('addresses'):
        formatted_info.append(f"Address: {locations['addresses']}")
    if locations.get('other_locations'):
        formatted_info.append(f"Other Locations: {locations['other_locations']}")
    
    # Other Data
    if extraction_result.get('other_data'):
        formatted_info.append(f"Other Structured Data: {extraction_result['other_data']}")
    
    return '\n'.join(formatted_info) if formatted_info else "No identifiable information found."

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
                             raw_text=extraction_result.get('text', ''),
                             formatted_info=format_extracted_info(extraction_result),
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
            'raw_text': extraction_result.get('text', ''),
            'formatted_info': format_extracted_info(extraction_result),
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