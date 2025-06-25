#!/usr/bin/env python3
"""
Tesseract OCR Installation Helper for Windows
"""

import os
import sys
import webbrowser
import subprocess
import platform

def check_tesseract():
    """Check if Tesseract is already installed"""
    try:
        return True
    except:
        print("❌ Tesseract OCR is not installed or not in PATH")
        return False

def check_system():
    """Check system information"""
    system = platform.system()
    print(f"🖥️  System: {system} {platform.release()}")
    
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"

def install_windows():
    """Guide Windows installation"""
    print("\n🔧 Installing Tesseract OCR on Windows:")
    print("=" * 50)
    
    print("📥 Step 1: Download Tesseract")
    print("   Opening download page in your browser...")
    
    # Open download page
    webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki")
    
    print("\n📋 Follow these steps:")
    print("   1. Download the latest Windows installer (.exe file)")
    print("   2. Run the installer as Administrator")
    print("   3. ⚠️  IMPORTANT: Check 'Add Tesseract to PATH' during installation")
    print("   4. Complete the installation")
    print("   5. Restart your terminal/command prompt")
    print("   6. Run this script again to verify installation")

def install_macos():
    """Guide macOS installation"""
    print("\n🔧 Installing Tesseract OCR on macOS:")
    print("=" * 50)
    
    print("📦 Using Homebrew (recommended):")
    print("   Run: brew install tesseract")
    
    print("\n📦 Alternative - MacPorts:")
    print("   Run: sudo port install tesseract")

def install_linux():
    """Guide Linux installation"""
    print("\n🔧 Installing Tesseract OCR on Linux:")
    print("=" * 50)
    
    print("📦 Ubuntu/Debian:")
    print("   Run: sudo apt-get update && sudo apt-get install tesseract-ocr")
    
    print("\n📦 CentOS/RHEL:")
    print("   Run: sudo yum install tesseract")
    
    print("\n📦 Fedora:")
    print("   Run: sudo dnf install tesseract")

def verify_installation():
    """Verify Tesseract installation"""
    print("\n🔍 Verifying installation...")
    
    # Check PATH
    try:
        result = subprocess.run(["tesseract", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract is in PATH")
            print(f"📄 Version info: {result.stdout.split(chr(10))[0]}")
            return True
        else:
            print("❌ Tesseract not found in PATH")
            return False
    except FileNotFoundError:
        print("❌ Tesseract command not found")
        return False

def main():
    """Main installation helper"""
    print("🚀 Tesseract OCR Installation Helper")
    print("=" * 50)
    
    # Check if already installed
    if check_tesseract():
        print("\n🎉 Great! Tesseract is working properly.")
        print("   You can now use the OCR feature in the web app!")
        return
    
    # Check system
    system = check_system()
    
    print(f"\n📋 Installation instructions for your system:")
    
    if system == "windows":
        install_windows()
    elif system == "macos":
        install_macos()
    elif system == "linux":
        install_linux()
    else:
        print("❓ Unknown system. Please check Tesseract documentation.")
        webbrowser.open("https://github.com/tesseract-ocr/tesseract")
    
    print(f"\n⏳ After installation, run this script again to verify:")
    print(f"   python {__file__}")
    
    # Try to verify if on Windows and user wants to test
    if system == "windows":
        input("\n⏸️  Press Enter after you've completed the installation to verify...")
        if verify_installation():
            print("\n🎉 Perfect! Tesseract is now installed and working!")
            print("   You can now use the OCR feature in the web app!")
        else:
            print("\n🔧 Installation verification failed.")
            print("   Please make sure:")
            print("   1. You ran the installer as Administrator")
            print("   2. You checked 'Add to PATH' during installation")
            print("   3. You restarted your terminal")

if __name__ == "__main__":
    main() 