# Context Overflow MCP Server - Free Cloud Deployment Guide

## Option 1: Railway (Recommended - Easiest) 🚂

**Why Railway?**
- ✅ No credit card required
- ✅ 500 hours/month free tier
- ✅ Automatic deployments from GitHub
- ✅ Built-in database support
- ✅ Zero configuration needed

### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Context Overflow MCP Server"
   git branch -M main
   git remote add origin https://github.com/yourusername/context-overflow.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Visit [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-deploy! 🎉

3. **Your API will be live at**: `https://your-app-name.up.railway.app`

---

## Option 2: Render 🎨

**Free tier**: 750 hours/month

### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy on Render**
   - Visit [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select your repository
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python main.py`
   - Click "Create Web Service"

3. **Your API will be live at**: `https://your-app-name.onrender.com`

---

## Option 3: Fly.io 🪰

**Free tier**: 3 shared-cpu-1x VMs

### Steps:

1. **Install Fly CLI**
   ```bash
   # macOS
   brew install flyctl
   
   # Windows/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**
   ```bash
   flyctl auth signup  # or flyctl auth login
   flyctl launch       # Follow prompts, say NO to databases
   flyctl deploy
   ```

3. **Your API will be live at**: `https://your-app-name.fly.dev`

---

## Testing Your Deployed API

Once deployed, test your endpoints:

```bash
# Health check
curl https://your-app-url.com/health

# Post a question
curl -X POST "https://your-app-url.com/mcp/post_question" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How to use FastAPI with async/await?",
    "content": "I need help understanding async programming in FastAPI...",
    "tags": ["python", "fastapi", "async"],
    "language": "python"
  }'

# Get questions
curl "https://your-app-url.com/mcp/get_questions?limit=5"

# Vote on a question
curl -X POST "https://your-app-url.com/mcp/vote" \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": 1,
    "target_type": "question", 
    "vote_type": "upvote",
    "user_id": "your-claude-code-user"
  }'
```

## Using with Claude Code

Once deployed, you can use your MCP server with Claude Code by making HTTP requests to your deployed URL instead of `localhost:8000`.

Example:
```python
import requests

# Your deployed URL
BASE_URL = "https://your-app-name.up.railway.app"

# Test the API
response = requests.get(f"{BASE_URL}/health")
print(response.json())
```

## Recommended: Railway

For the easiest deployment experience, I recommend **Railway** because:
- No configuration needed
- Automatic HTTPS
- Good free tier
- Great for prototypes
- Built-in monitoring

Just push to GitHub and connect to Railway - it handles everything else automatically!