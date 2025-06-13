# Image Text Recognition Web App

A modern, user-friendly web application built with Flask that extracts text from images using OCR (Optical Character Recognition) technology. The app supports both free local OCR via Tesseract and advanced AI-powered text recognition via OpenAI's Vision API.

## ✨ Features

- **Drag & Drop Interface**: Modern, intuitive file upload with drag-and-drop support
- **Multiple OCR Methods**: 
  - **Tesseract OCR**: Free, open-source OCR engine (works locally)
  - **OpenAI Vision API**: Advanced AI model for complex layouts and handwriting
- **Real-time Processing**: Instant text extraction with progress indicators
- **Text Management**: Copy, download, and share extracted text
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **API Endpoint**: RESTful API for programmatic access
- **File Type Support**: PNG, JPG, JPEG, GIF, BMP, TIFF

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Tesseract OCR** installed (for local OCR functionality)

#### Installing Tesseract OCR

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Setup

1. **Clone or download the project**
```bash
git clone <repository-url>
cd text_regonize
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration** (optional for OpenAI API)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key if you want to use AI recognition
# OPENAI_API_KEY=your_api_key_here
```

## 🚀 Usage

### Running the Application

1. **Start the Flask server**
```bash
python app.py
```

2. **Open your browser** and navigate to:
```
http://localhost:5000
```

### Using the Web Interface

1. **Upload an Image**: 
   - Drag and drop an image file onto the upload area, or
   - Click the upload area to browse and select a file

2. **Choose Recognition Method**:
   - **Tesseract OCR**: Free, works locally, good for clear printed text
   - **OpenAI Vision**: Advanced AI, requires API key, handles complex layouts

3. **Extract Text**: Click "Extract Text" and wait for processing

4. **Manage Results**: 
   - View extracted text with statistics
   - Copy text to clipboard
   - Download as TXT file
   - Share text (on supported devices)

### API Usage

The application also provides a RESTful API endpoint:

```bash
# POST /api/extract
curl -X POST -F "file=@image.jpg" -F "method=tesseract" http://localhost:5000/api/extract
```

**Response:**
```json
{
  "text": "Extracted text content...",
  "method": "tesseract",
  "filename": "image.jpg"
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### OpenAI API Setup

1. **Get API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Create new secret key**
3. **Add to .env file**: Set `OPENAI_API_KEY=your_key_here`
4. **Billing**: Ensure you have billing set up for API usage

## 📁 Project Structure

```
text_regonize/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with common layout
│   ├── index.html        # Main upload page
│   └── result.html       # Results display page
├── static/               # Static files (CSS, JS, images)
└── uploads/              # Temporary upload directory
```

## 🎯 Supported File Types

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff)

## 🔒 Security Features

- File type validation
- Secure filename handling
- File size limits (16MB max)
- Temporary file cleanup
- CSRF protection

## 🚀 Deployment

### Production Deployment

For production deployment, consider:

1. **Use a production WSGI server**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Set environment variables**:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
```

3. **Configure reverse proxy** (nginx, Apache)
4. **Set up SSL/HTTPS**
5. **Configure monitoring and logging**

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract not found error**:
   - Ensure Tesseract is installed and in PATH
   - On Windows, add Tesseract installation directory to PATH

2. **OpenAI API errors**:
   - Check API key is valid
   - Ensure billing is set up
   - Verify API usage limits

3. **File upload errors**:
   - Check file size (max 16MB)
   - Verify file type is supported
   - Ensure sufficient disk space

4. **Permission errors**:
   - Check write permissions for uploads directory
   - Run with appropriate user permissions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Open source OCR engine
- [OpenAI](https://openai.com/) - AI-powered text recognition
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - UI framework 