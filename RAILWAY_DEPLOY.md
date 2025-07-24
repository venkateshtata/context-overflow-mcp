# 🚂 Railway Deployment Guide - Context Overflow MCP Server

## Step 1: Create GitHub Repository

1. **Go to GitHub** (https://github.com)
2. **Click "New repository"** (green button)
3. **Repository settings:**
   - Repository name: `context-overflow-mcp`
   - Description: `Context Overflow MCP Server with voting system`
   - Set to **Public** (required for Railway free tier)
   - **DON'T** initialize with README, .gitignore, or license
4. **Click "Create repository"**

## Step 2: Push Your Code to GitHub

Copy and paste these commands one by one in your terminal:

```bash
# Navigate to your project directory (if not already there)
cd /Users/venkat/context_overflow

# Add your GitHub repository as remote origin
git remote add origin https://github.com/YOUR_USERNAME/context-overflow-mcp.git

# Push your code to GitHub
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

## Step 3: Deploy on Railway

1. **Go to Railway** (https://railway.app)

2. **Sign up/Login:**
   - Click "Login" in top right
   - Choose "Login with GitHub" (recommended)
   - Authorize Railway to access your GitHub

3. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Find and select your `context-overflow-mcp` repository
   - Click "Deploy Now"

4. **Railway will automatically:**
   - ✅ Detect it's a Python project
   - ✅ Install dependencies from requirements.txt
   - ✅ Start your server with the Procfile
   - ✅ Assign a public URL

5. **Get Your URL:**
   - Click on your project
   - Go to "Settings" tab
   - Find "Public Networking" section
   - Your URL will be something like: `https://context-overflow-mcp-production.up.railway.app`

## Step 4: Verify Deployment

Wait 2-3 minutes for deployment to complete, then click your Railway URL. You should see:

```json
{"message": "Context Overflow MCP Server", "status": "running"}
```

## That's it! 🎉

Your MCP server is now live and ready to use with Claude Code!

---

## Troubleshooting

If deployment fails:

1. **Check the logs:**
   - Go to your Railway project
   - Click "Deployments" tab
   - Click on the failed deployment
   - Check the build/deploy logs

2. **Common issues:**
   - Make sure repository is **public**
   - Verify all files are committed to GitHub
   - Check that requirements.txt is in the root directory

3. **Redeploy:**
   - Make changes and push to GitHub
   - Railway will automatically redeploy