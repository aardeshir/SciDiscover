# Deployment Guide for SciDiscover

This document provides detailed instructions for deploying the SciDiscover platform via different methods.

## GitHub Deployment

### Prerequisites

- A GitHub account
- Git installed on your local machine
- Access to the SciDiscover codebase

### Deployment Steps

1. **Clone the repository locally**:
   ```bash
   git clone https://github.com/aardeshir/SciDiscover.git
   cd SciDiscover
   ```

2. **Set up your API keys**:
   - Create a `.env` file from the template
   ```bash
   cp .env.example .env
   ```
   - Edit the `.env` file to add your Anthropic API key
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Test locally before deployment**:
   ```bash
   streamlit run main.py
   ```

4. **Deploy to GitHub**:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

## Streamlit Cloud Deployment

Streamlit Cloud offers a zero-configuration hosting solution for Streamlit apps directly from GitHub.

1. **Sign up for [Streamlit Cloud](https://streamlit.io/cloud)**
2. **Connect your GitHub repository**
3. **Configure the app settings**:
   - Set the main file path to `main.py`
   - Add the `ANTHROPIC_API_KEY` as a secret in the Streamlit Cloud dashboard
4. **Deploy the app**

Your app will be deployed with a public URL in the format: `https://[your-app-name].streamlit.app`

## Docker Deployment

For containerized deployment in various environments:

1. **Build the Docker image**:
   ```bash
   docker build -t scidiscover:latest .
   ```

2. **Run as a container**:
   ```bash
   docker run -p 5000:5000 -e ANTHROPIC_API_KEY=your_key_here scidiscover:latest
   ```

3. **For cloud deployment (e.g., AWS, GCP, Azure)**:
   - Push the image to a container registry
   - Deploy using your cloud provider's container service
   - Ensure proper environment variable configuration

## Environment Variables

The following environment variables can be configured:

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude access | Yes |
| `OPENAI_API_KEY` | OpenAI API key for fallback capability | No |
| `ANTHROPIC_MODEL` | Specific Claude model to use | No |
| `HIGH_THINKING_TOKENS` | Token limit for high demand mode | No |
| `LOW_THINKING_TOKENS` | Token limit for low demand mode | No |
| `ENABLE_PERFORMANCE_TRACKING` | Enable/disable performance metrics | No |

## Security Considerations

1. **API Keys**: Never commit API keys to version control. Always use environment variables or secrets management.
2. **Access Control**: Consider implementing authentication if your deployment contains sensitive research information.
3. **Rate Limiting**: Be aware of API rate limits when using LLM services in a production environment.

## Troubleshooting

- **API Errors**: Ensure your API keys are correctly configured and not expired
- **Memory Issues**: Adjust the thinking tokens if experiencing out-of-memory errors
- **Deployment Failures**: Check logs for specific error messages, which are commonly related to missing dependencies or configuration issues

## Support

For deployment issues, please open an issue on the GitHub repository: https://github.com/aardeshir/SciDiscover/issues