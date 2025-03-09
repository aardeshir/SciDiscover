# SciDiscover

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## An Advanced Scientific Discovery Platform

SciDiscover is a cutting-edge platform for scientific discovery that leverages multi-agent AI reasoning to transform biomedical research through intelligent, adaptive knowledge exploration and collaborative hypothesis generation.

![SciDiscover Interface](resources/scidiscover_interface.png)

## Core Features

- **Multi-Agent Reasoning**: Implements a collaborative multi-agent framework with specialized agents for hypothesis generation, critique, and refinement
- **Dynamic Knowledge Graphs**: Visualizes and navigates complex relationships between scientific concepts
- **Extended Thinking Capabilities**: Utilizes Claude 3.7 Sonnet's advanced reasoning for deeper scientific analysis
- **Performance Metrics**: Tracks analysis time and confidence scores for experimental validation
- **Debate-Driven Analysis**: Simulates scientific discourse through structured multi-agent debate

## Technologies

- **Backend**: Python with advanced LLM integration (Claude 3.7 Sonnet)
- **Frontend**: Streamlit interactive web interface
- **Data Sources**: Integration with PubTator3 for entity recognition
- **Knowledge Integration**: Custom knowledge graph construction

## Getting Started

### Prerequisites

- Python 3.11+
- Streamlit
- Anthropic API key
- OpenAI API key (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/ArdeshirLab/scidiscover.git
cd scidiscover

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Option 1: Using .env file (recommended)
cp .env.example .env
# Edit .env file with your API keys

# Option 2: Setting environment variables directly
export ANTHROPIC_API_KEY=your_anthropic_api_key
export OPENAI_API_KEY=your_openai_api_key  # Optional
```

#### API Keys

SciDiscover requires an Anthropic API key to function properly. Follow these steps to set up your API keys:

1. Create an account on [Anthropic's website](https://console.anthropic.com/)
2. Generate an API key from the Anthropic console
3. Copy the `.env.example` file to `.env` and add your key:
   ```
   ANTHROPIC_API_KEY=your_actual_key_here
   ```

Note: OpenAI API key is optional and only used as a fallback if specified.

### Running the Application

```bash
streamlit run main.py
```

The application will be available at http://localhost:5000

## Usage Guide

### Performing Scientific Analysis

1. Enter your scientific query in the main text area
2. Adjust the novelty level slider (0: established knowledge, 1: cutting-edge)
3. Select your preferred analysis method:
   - Standard Analysis: Direct exploration of mechanisms
   - Debate-Driven Analysis: Multi-agent collaborative reasoning
4. Choose the appropriate thinking mode based on query complexity:
   - High-Demand: 64K thinking tokens (best for complex queries)
   - Low-Demand: 32K thinking tokens (balanced)
   - None: Standard processing (fastest)
5. Click "Analyze" to initiate the discovery process

### Interpreting Results

The analysis results include:
- Key molecular pathways
- Relevant genes and their roles
- Detailed molecular mechanisms
- Temporal sequence of events
- Supporting experimental evidence
- Clinical and therapeutic implications
- Confidence score and analysis metrics

## Architecture

SciDiscover is built with a modular architecture:

- **Knowledge Layer**: Entity recognition, knowledge graph construction
- **Reasoning Layer**: LLM-based agents, hypothesis generation, validation
- **Orchestration Layer**: Workflow management, agent coordination
- **User Interface**: Interactive visualization, configuration controls

## Development

### Project Structure

```
scidiscover/
├── knowledge/        # Knowledge integration components
├── reasoning/        # AI reasoning and hypothesis generation
├── orchestrator/     # Scientific workflow coordination
├── ui/               # Streamlit interface components
├── config.py         # Configuration settings
└── snapshot.py       # Versioning and snapshot management
```

### Snapshot System

SciDiscover includes a snapshot system for versioning analyses:

```bash
# Create a new snapshot
python scripts/create_snapshot.py create "My Research Milestone" --description "Key findings on mechanism X"

# List all snapshots
python scripts/create_snapshot.py list

# Show snapshot details
python scripts/create_snapshot.py show "My Research Milestone"
```

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Acknowledgments

- This research utilizes the Anthropic Claude API
- PubTator3 for biomedical entity recognition
- NetworkX for knowledge graph implementations

## Contact

For questions or collaboration opportunities, please reach out to the ArdeshirLab organization.