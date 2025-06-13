#!/usr/bin/env python3
"""
Helper script to install Japanese language data for Tesseract OCR
"""

import os
import sys
import platform
import urllib.request
import shutil
import subprocess

def find_tesseract_path():
    """Find Tesseract installation path"""
    system = platform.system()
    
    if system == "Windows":
        common_paths = [
            "C:\\Program Files\\Tesseract-OCR",
            "C:\\Program Files (x86)\\Tesseract-OCR",
            "C:\\Users\\%s\\AppData\\Local\\Tesseract-OCR" % os.getenv('USERNAME', ''),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
                
        # Try to find via where command
        try:
            result = subprocess.run(["where", "tesseract"], capture_output=True, text=True)
            if result.returncode == 0:
                tesseract_exe = result.stdout.strip().split('\n')[0]
                return os.path.dirname(tesseract_exe)
        except:
            pass
            
    elif system == "Darwin":  # macOS
        common_paths = [
            "/usr/local/share/tessdata",
            "/opt/homebrew/share/tessdata",
            "/usr/share/tessdata"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return os.path.dirname(path)
    
    elif system == "Linux":
        common_paths = [
            "/usr/share/tesseract-ocr",
            "/usr/share/tessdata"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path if path.endswith('tessdata') else path
    
    return None

def download_japanese_data(tessdata_path):
    """Download Japanese language data"""
    print("📥 Downloading Japanese language data...")
    
    url = "https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata"
    jpn_file_path = os.path.join(tessdata_path, "jpn.traineddata")
    
    try:
        print(f"   Downloading from: {url}")
        print(f"   Saving to: {jpn_file_path}")
        
        urllib.request.urlretrieve(url, jpn_file_path)
        print("✅ Japanese language data downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error downloading Japanese data: {e}")
        return False

def verify_japanese_support():
    """Verify Japanese language support"""
    try:
        import pytesseract
        
        # Try to get available languages
        langs = pytesseract.get_languages()
        if 'jpn' in langs:
            print("✅ Japanese language support verified!")
            return True
        else:
            print("❌ Japanese language not found in available languages")
            print(f"   Available languages: {', '.join(langs)}")
            return False
    except Exception as e:
        print(f"❌ Error verifying Japanese support: {e}")
        return False

def main():
    """Main installation function"""
    print("🔧 Japanese Language Data Installer for Tesseract OCR")
    print("=" * 60)
    
    # Check if Tesseract is installed
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR found! Version: {version}")
    except:
        print("❌ Tesseract OCR is not installed or not accessible")
        print("   Please install Tesseract first before running this script")
        return
    
    # Check if Japanese is already available
    if verify_japanese_support():
        print("\n🎉 Japanese language support is already available!")
        return
    
    print("\n🔍 Searching for Tesseract installation...")
    tesseract_path = find_tesseract_path()
    
    if not tesseract_path:
        print("❌ Could not find Tesseract installation path")
        print("\n💡 Manual installation:")
        print("1. Download jpn.traineddata from: https://github.com/tesseract-ocr/tessdata")
        print("2. Copy it to your Tesseract tessdata folder")
        print("3. Common locations:")
        print("   - Windows: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
        print("   - macOS: /usr/local/share/tessdata/")
        print("   - Linux: /usr/share/tessdata/")
        return
    
    print(f"✅ Found Tesseract at: {tesseract_path}")
    
    # Find tessdata directory
    tessdata_path = os.path.join(tesseract_path, "tessdata")
    if not os.path.exists(tessdata_path):
        print(f"❌ tessdata directory not found at: {tessdata_path}")
        return
    
    print(f"✅ tessdata directory: {tessdata_path}")
    
    # Check if jpn.traineddata already exists
    jpn_file = os.path.join(tessdata_path, "jpn.traineddata")
    if os.path.exists(jpn_file):
        print("✅ jpn.traineddata already exists!")
        if not verify_japanese_support():
            print("⚠️  File exists but Japanese support not working. You may need to restart your application.")
        return
    
    # Check write permissions
    if not os.access(tessdata_path, os.W_OK):
        print(f"❌ No write permission to {tessdata_path}")
        print("💡 Try running this script as administrator/sudo")
        return
    
    # Download Japanese data
    if download_japanese_data(tessdata_path):
        print("\n🔍 Verifying installation...")
        if verify_japanese_support():
            print("\n🎉 Japanese language support installed successfully!")
            print("   You can now use Japanese OCR in the web app!")
        else:
            print("\n⚠️  Installation completed but verification failed.")
            print("   You may need to restart your application.")
    else:
        print("\n❌ Installation failed. Please try manual installation.")

if __name__ == "__main__":
    main() 