# 🚀 Railway Quick Setup

## Required Environment Variables

Add these in Railway Dashboard > Variables:

```bash
# Core settings
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-to-something-long-and-random

# OpenAI API (optional but recommended)
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## Generate SECRET_KEY

You can generate a secure secret key using Python:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Expected Build Output

✅ **Successful build should show:**
```
Building image...
Installing dependencies...
✓ Successfully built image
✓ Deployment successful
✓ Service is live at: https://your-app.up.railway.app
```

## Test URLs after deployment:

- **Main page**: `https://your-app.up.railway.app/`
- **API endpoint**: `https://your-app.up.railway.app/api/extract`

## Troubleshooting

If build fails:
1. Check build logs in Railway dashboard
2. Verify Dockerfile syntax
3. Check if all dependencies are in requirements.txt
4. Ensure environment variables are set correctly 