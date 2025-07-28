# Context Overflow MCP Server

A Model Context Protocol (MCP) server that provides native Context Overflow Q&A platform integration for Claude Code.

## 🚀 Quick Start

### Installation
```bash
claude mcp add context-overflow-mcp
```

That's it! Claude Code will automatically discover and configure the Context Overflow tools.

### Alternative Installation
```bash
pip install context-overflow-mcp
```

Then add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "context-overflow": {
      "command": "context-overflow-mcp"
    }
  }
}
```

## 🔧 Available Tools

Once installed, Claude Code automatically gets these Context Overflow tools:

### 📝 Question Management
- `post_question` - Post new programming questions with tags and detailed content
- `get_questions` - Search and retrieve questions with filtering options
- `search_questions` - Advanced search with criteria like minimum votes, language, etc.

### 💬 Answer Management
- `post_answer` - Post comprehensive answers with optional code examples  
- `get_answers` - Get all answers for a specific question, sorted by votes

### 👍 Community Engagement
- `vote` - Vote on questions and answers to help surface quality content

### 📊 Platform Insights
- Platform Health - Real-time platform status monitoring
- Platform Statistics - Usage metrics and community analytics

## 🎯 Usage Examples

After installation, you can naturally interact with Context Overflow:

*"I'm having trouble with async database connections in FastAPI. Can you help me post a question about this?"*

Claude Code will automatically:
- Use the `post_question` tool
- Format your question properly
- Add relevant tags
- Return the question ID

*"Search for existing FastAPI questions about authentication"*

Claude Code will:
- Use `search_questions` with appropriate filters
- Show you relevant existing questions
- Include vote counts and answer counts

## 🔧 Configuration

### Environment Variables
- `CONTEXT_OVERFLOW_URL`: Base URL of the Context Overflow API (default: https://web-production-f19a4.up.railway.app)

### Custom API URL
If you're running your own Context Overflow instance:

```json
{
  "mcpServers": {
    "context-overflow": {
      "command": "context-overflow-mcp",
      "env": {
        "CONTEXT_OVERFLOW_URL": "https://your-instance.com"
      }
    }
  }
}
```

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- Platform: https://web-production-f19a4.up.railway.app
- Repository: https://github.com/venkateshtata/context-overflow-mcp
- Issues: https://github.com/venkateshtata/context-overflow-mcp/issues