# Security Policy

## API Key Security

SciDiscover requires API keys to function properly. Follow these security practices:

1. **Never commit API keys to the repository**
   - Always use environment variables or `.env` files (not checked into version control)
   - The `.env` file is listed in `.gitignore` to prevent accidental commits

2. **Environment Variable Security**
   - Set API keys as environment variables in your deployment environment
   - For local development, use the `.env` file (copy from `.env.example` and add your keys)

3. **Claude API Key**
   - Required for core functionality
   - Stored as `ANTHROPIC_API_KEY` environment variable
   - Create your API key at: https://console.anthropic.com/

4. **OpenAI API Key (Optional)**
   - Only used as a fallback if specified
   - Stored as `OPENAI_API_KEY` environment variable

## Token Usage and Rate Limiting

SciDiscover is designed for high token usage tasks:

- High Thinking Mode: Uses up to 64K thinking tokens + 80K output tokens
- Low Thinking Mode: Uses up to 32K thinking tokens + 64K output tokens
- Standard Mode: Uses up to 32K output tokens

Be aware of your API rate limits and token quotas when using the application, especially for complex scientific queries.

## Data Privacy

SciDiscover processes all scientific queries through external API services (Anthropic Claude and optionally OpenAI). Be mindful of the following:

1. **Scientific Query Data**: All data sent to the scientific analysis will be processed by the chosen API service
2. **Thinking Logs**: Logs of the thinking process are stored locally in `claude_thinking_log.txt`
3. **Local Caching**: Some data may be cached locally for performance

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by:

1. Creating an issue in the GitHub repository
2. For sensitive vulnerabilities, contact the repository maintainers directly

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fixes (if any)

We take security issues seriously and will respond promptly to all reports.