#!/usr/bin/env python3
"""
Quick start script for the Image Text Recognition Web App
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check if requirements are installed
    try:
        import flask
        import PIL
        import pytesseract
        print("✅ Core dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please run: pip install -r requirements.txt")
        return False
    
    # Check Tesseract
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR found")
    except Exception:
        print("⚠️  Tesseract OCR not found - OCR functionality will be limited")
        print("💡 Install Tesseract: https://github.com/tesseract-ocr/tesseract")
    
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['uploads', 'templates', 'static']
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def main():
    """Main function to start the application"""
    print("🚀 Starting Image Text Recognition Web App")
    print("=" * 50)
    
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install requirements first.")
        sys.exit(1)
    
    create_directories()
    
    print("\n✅ All checks passed!")
    print("🌐 Starting Flask server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 