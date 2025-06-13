#!/usr/bin/env python3
"""
Debug test for Japanese OCR
"""

import os
import sys
import pytesseract
from PIL import Image, ImageDraw

print("🔍 Debug Test for Japanese OCR")
print("=" * 50)

# Check environment
print(f"Python version: {sys.version}")
print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")

# Check Tesseract
try:
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract version: {version}")
except Exception as e:
    print(f"❌ Tesseract error: {e}")
    sys.exit(1)

# Check languages
try:
    languages = pytesseract.get_languages()
    print(f"Available languages: {languages}")
    
    if 'jpn' in languages:
        print("✅ Japanese language found!")
        
        # Create a simple test image with ASCII text first
        print("\n📝 Creating test image...")
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Use simple ASCII text for testing
        test_text = "Hello World"
        draw.text((50, 30), test_text, fill='black')
        img.save('test_eng.png')
        
        # Test English first
        print("🔍 Testing English OCR...")
        try:
            result_eng = pytesseract.image_to_string(img, lang='eng')
            print(f"English result: '{result_eng.strip()}'")
        except Exception as e:
            print(f"❌ English OCR error: {e}")
        
        # Test Japanese with explicit tessdata path
        print("🔍 Testing Japanese OCR with explicit path...")
        try:
            config = '--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"'
            result_jpn = pytesseract.image_to_string(img, lang='jpn', config=config)
            print(f"Japanese OCR result: '{result_jpn.strip()}'")
            print("✅ Japanese OCR executed successfully!")
        except Exception as e:
            print(f"❌ Japanese OCR error: {e}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            
        # Also try without explicit path
        print("🔍 Testing Japanese OCR without explicit path...")
        try:
            result_jpn2 = pytesseract.image_to_string(img, lang='jpn')
            print(f"Japanese OCR result (no path): '{result_jpn2.strip()}'")
            print("✅ Japanese OCR without path executed successfully!")
        except Exception as e:
            print(f"❌ Japanese OCR without path error: {e}")
        
        # Clean up
        if os.path.exists('test_eng.png'):
            os.remove('test_eng.png')
            
    else:
        print("❌ Japanese language not found!")
        
except Exception as e:
    print(f"❌ Language check error: {e}")

print("\n" + "=" * 50)
print("Debug test completed!") 