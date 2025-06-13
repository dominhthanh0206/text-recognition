# 🖥️ Setup Guide for New Machine

## 📋 **Requirements**

### **Required:**
- Python 3.8+ 
- Git
- Internet connection

### **Optional (for Tesseract OCR):**
- Tesseract OCR binary
- Japanese language data

---

## 🚀 **Quick Setup (Any Machine)**

### **1. Clone repository:**
```bash
git clone https://github.com/your-username/text-recognition.git
cd text-recognition
```

### **2. Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **3. Install dependencies:**
```bash
pip install -r requirements.txt
```

### **4. Run application:**
```bash
python app.py
```

**✅ App will run at: http://localhost:5000**

---

## 🎯 **Configuration Options**

### **Option 1: OpenAI Vision Only (Recommended)**
- ✅ **Works on ANY machine** with internet
- ✅ **No additional setup** needed
- ✅ **Better accuracy** for complex images
- 💰 **Cost**: ~$0.01-0.02 per image

**Setup:**
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### **Option 2: Tesseract OCR**
- ✅ **Free processing**
- ❌ **Requires system installation**
- ❌ **Platform-specific setup**

---

## 🔧 **Tesseract Setup by Platform**

### **Windows:**
```bash
# Download and install from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Or use chocolatey:
choco install tesseract
```

### **macOS:**
```bash
# Using Homebrew:
brew install tesseract tesseract-lang

# Or MacPorts:
sudo port install tesseract +all_langs
```

### **Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

### **Linux (CentOS/RHEL):**
```bash
sudo yum install tesseract tesseract-langpack-jpn
```

---

## 🌍 **Cross-Platform Compatibility**

| Feature | Windows | macOS | Linux | Docker |
|---------|---------|-------|-------|--------|
| **Flask App** | ✅ | ✅ | ✅ | ✅ |
| **OpenAI Vision** | ✅ | ✅ | ✅ | ✅ |
| **Tesseract OCR** | ⚠️ | ⚠️ | ⚠️ | ✅ |
| **Japanese Support** | ⚠️ | ⚠️ | ⚠️ | ✅ |

**Legend:**
- ✅ Works out of box
- ⚠️ Needs additional setup

---

## 🐳 **Docker Solution (Best for Portability)**

### **Run with Docker:**
```bash
# Build image
docker build -t text-recognition .

# Run container
docker run -p 5000:5000 -e OPENAI_API_KEY=your-key text-recognition
```

### **Benefits:**
- ✅ **Same environment** everywhere
- ✅ **All dependencies** included
- ✅ **No manual setup** needed
- ✅ **Works on** Windows, macOS, Linux

---

## ☁️ **Cloud Deployment Options**

### **1. Railway (Current)**
- ✅ **Zero config** deployment
- ✅ **Auto HTTPS**
- ✅ **Global CDN**

### **2. Other Platforms:**
- **Heroku**: Similar to Railway
- **Vercel**: Good for frontend
- **DigitalOcean App Platform**: Good for production
- **AWS/GCP/Azure**: Full control

---

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **Import errors:**
```bash
# Solution: Install missing packages
pip install -r requirements.txt
```

#### **Tesseract not found:**
```bash
# Windows: Add to PATH
# macOS/Linux: Install via package manager
```

#### **Japanese not working:**
```bash
# Download language data manually:
# https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata
```

#### **Port already in use:**
```bash
# Change port in app.py:
app.run(port=5001)
```

---

## 📱 **Mobile/Tablet Access**

### **Local network access:**
```bash
# Run with host binding:
python app.py  # Already configured for 0.0.0.0

# Access from other devices:
http://YOUR_IP_ADDRESS:5000
```

### **Find your IP:**
```bash
# Windows:
ipconfig

# macOS/Linux:
ifconfig
```

---

## 🚀 **Production Deployment Checklist**

- [ ] Set `SECRET_KEY` environment variable
- [ ] Set `FLASK_ENV=production`
- [ ] Configure HTTPS (auto on Railway/Heroku)
- [ ] Set up monitoring/logging
- [ ] Configure backup strategy
- [ ] Test with real data

---

## 📊 **Performance Expectations**

| Method | Local Speed | Cloud Speed | Memory Usage |
|--------|-------------|-------------|--------------|
| **OpenAI Vision** | Fast | Fast | Low (~100MB) |
| **Tesseract** | Medium | Slow | High (~500MB) |

---

## 🔒 **Security Considerations**

### **For production:**
- Use strong `SECRET_KEY`
- Enable HTTPS only
- Rate limiting
- Input validation
- File size limits (already implemented)

### **For development:**
- Keep API keys secure
- Use `.env` files
- Don't commit secrets to git 