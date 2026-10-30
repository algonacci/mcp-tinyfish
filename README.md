# mcp-tinyfish

MCP server for TinyFish web search and page extraction.

## Setup

```bash
cp .env.example .env
# Add TINYFISH_API_KEY to .env
uv sync
```

Register in an MCP client:

```json
{
  "mcpServers": {
    "tinyfish": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-tinyfish", "run", "main.py"]
    }
  }
}
```

## Tools

- `tinyfish_search`: ranked web results with domain, location, and language filters; capped at 20 results.
- `tinyfish_fetch`: fetch up to 10 public HTTP(S) URLs as Markdown, text, or HTML.

TinyFish currently documents 12,000 free search requests per day and a default personal limit of 30 requests per minute. Provider terms may change.
