# 🚀 Railway Deployment Guide

## 📋 **Tổng quan**

Project này có thể được deploy lên Railway với 2 options:
1. **OpenAI Vision API only** (Khuyến nghị - Nhẹ, nhanh)
2. **Tesseract + Japanese support** (Nặng hơn, chậm hơn)

## 🎯 **Option 1: OpenAI Vision API (Khuyến nghị)**

### **Ưu điểm:**
- ✅ Build time nhanh (~2-3 phút)
- ✅ Container size nhỏ (~200MB)
- ✅ Hiệu suất cao
- ✅ Hỗ trợ nhiều ngôn ngữ tự động
- ✅ Chính xác cao hơn

### **Setup:**

1. **Rename Dockerfile:**
   ```bash
   # Sử dụng Dockerfile mặc định (không có Tesseract)
   # File Dockerfile đã được tạo sẵn
   ```

2. **Environment Variables trong Railway:**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_ENV=production
   SECRET_KEY=your_production_secret_key
   ```

3. **Deploy steps:**
   - Connect GitHub repo to Railway
   - Set environment variables
   - Deploy sẽ tự động build

### **Chi phí:**
- Railway: Free tier hoặc $5/month
- OpenAI API: ~$0.01-0.02 per request

---

## 🔧 **Option 2: Tesseract + Japanese**

### **Ưu điểm:**
- ✅ Không phụ thuộc external API
- ✅ Miễn phí OCR
- ✅ Hoạt động offline

### **Nhược điểm:**
- ❌ Build time lâu (~5-10 phút)
- ❌ Container size lớn (~800MB)
- ❌ Memory usage cao
- ❌ Có thể gặp timeout trên Railway free tier

### **Setup:**

1. **Rename Dockerfile:**
   ```bash
   mv Dockerfile Dockerfile.openai
   mv Dockerfile.tesseract Dockerfile
   ```

2. **Environment Variables trong Railway:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your_production_secret_key
   TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
   ```

3. **Deploy steps:**
   - Connect GitHub repo to Railway
   - Set environment variables
   - Build sẽ mất 5-10 phút
   - Container sẽ nặng ~800MB

---

## 🚀 **Deployment Steps (Chi tiết)**

### **1. Prepare Repository:**

```bash
# Clone project
git clone your-repository
cd text_regonize

# Add files to git
git add .
git commit -m "Add Railway deployment files"
git push origin main
```

### **2. Railway Setup:**

1. **Tạo account Railway:** https://railway.app/
2. **New Project > Deploy from GitHub**
3. **Connect repository**
4. **Set Environment Variables:**
   - Go to Variables tab
   - Add required environment variables

### **3. Domain Setup:**

Railway sẽ tự động tạo domain:
```
https://your-project-name.up.railway.app
```

### **4. Monitoring:**

- Check build logs trong Railway dashboard
- Monitor resource usage
- Set up alerts nếu cần

---

## 📊 **So sánh chi tiết:**

| Feature | OpenAI Vision | Tesseract |
|---------|---------------|-----------|
| Build Time | 2-3 phút | 5-10 phút |
| Container Size | ~200MB | ~800MB |
| Memory Usage | Low | High |
| CPU Usage | Low | High |
| Accuracy | Very High | Good |
| Language Support | Auto-detect | Manual config |
| Cost | API cost | Free |
| Railway Compatibility | Excellent | Good |

---

## ⚡ **Khuyến nghị cho Railway:**

### **Cho development/testing:**
- Sử dụng **Option 1 (OpenAI Vision)**
- Setup nhanh, ít lỗi

### **Cho production scale nhỏ:**
- Sử dụng **Option 1 (OpenAI Vision)**
- Tối ưu cost và performance

### **Cho production scale lớn hoặc privacy concerns:**
- Xem xét **Option 2 (Tesseract)**
- Hoặc deploy trên VPS/dedicated server

---

## 🔧 **Troubleshooting:**

### **Build fails với Tesseract:**
```bash
# Kiểm tra Dockerfile.tesseract
# Có thể cần update package versions
```

### **Out of memory:**
```bash
# Railway free tier có limit memory
# Upgrade plan hoặc optimize code
```

### **Japanese không hoạt động:**
```bash
# Check TESSDATA_PREFIX environment variable
# Verify language files downloaded correctly
```

---

## 📞 **Support:**

- Railway docs: https://docs.railway.app/
- OpenAI API docs: https://platform.openai.com/docs/
- Tesseract docs: https://tesseract-ocr.github.io/ 