# Contributing to SciDiscover

Thank you for your interest in contributing to SciDiscover! This document outlines the process for contributing to the project.

## Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/scidiscover.git
   cd scidiscover
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements_dev.txt
   ```

4. **Set up API keys**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Development Workflow

1. **Create a new branch for your feature or bugfix**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and linting**
   ```bash
   # Run tests
   pytest
   
   # Run code formatting
   black .
   
   # Run linting
   flake8
   ```

4. **Create a snapshot for significant changes**
   ```bash
   python scripts/create_snapshot.py create "Feature Name" --description "Brief description"
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

6. **Submit a pull request**
   - Push your branch to your fork
   - Create a pull request to the main repository
   - Describe your changes in detail

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use type hints wherever possible
- Document all functions, classes, and modules following the existing style
- Keep functions focused on a single responsibility
- Write tests for new functionality

## API Design Guidelines

When extending the SciAgent system or adding new agents:

1. **Agent Interface Consistency**
   - All agents should follow the existing agent interface pattern
   - Methods should have clear input/output contracts

2. **LLM Prompting**
   - Use structured, detailed prompts with clear instructions
   - Include error handling for LLM responses

3. **Knowledge Graph Integration**
   - When adding new knowledge sources, integrate with the existing graph structure
   - Maintain compatibility with the KG-COI methodology

## Testing Guidelines

- Write unit tests for new functionality
- Test edge cases and error conditions
- Use pytest fixtures for shared test setups
- Mock external API calls when testing

## Documentation Guidelines

- Update README.md for user-facing changes
- Document new configuration options in both code and documentation
- Include examples of usage for new features
- Update architecture diagrams if necessary

Thank you for contributing to SciDiscover!