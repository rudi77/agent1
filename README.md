# LLM Repository Agent

A powerful AI-powered agent for automating repository creation and code generation, leveraging Large Language Models (LLMs) to create fully functional codebases based on user requirements.

## Overview

The LLM Repository Agent is designed to streamline the initial setup of new software projects by automating the creation of repositories, generating source code, and producing comprehensive documentation. It uses language-specific templates to ensure architectural consistency and best practices across different programming languages.

## Features

- **Automated Repository Setup**: Initializes Git repositories and manages version control operations
- **Template-Based Generation**: Uses language-specific templates to ensure consistent project structure
- **Multi-Language Support**: Currently supports Python and C# with extensibility for other languages
- **Complete Code Generation**: Autonomously generates all necessary source code based on requirements
- **Documentation Generation**: Creates comprehensive documentation including READMEs and architecture docs
- **Best Practices**: Enforces coding standards and architectural patterns based on provided templates

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-repo-agent
```

2. Install dependencies using pip:
```bash
pip install -r requirements.txt
```

Or using the project's pyproject.toml:
```bash
pip install .
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```env
OPENAI_API_KEY=your_api_key_here
```

## Installation with uv

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver, written in Rust. Here's how to set up the project using uv:

1. Install uv if you haven't already:
```bash
pip install uv
```

2. Create and activate a virtual environment:
```bash
uv venv
# On Windows:
.venv\Scripts\activate
# On Unix-like systems:
source .venv/bin/activate
```

3. Install dependencies using uv:
```bash
# Install from requirements.txt
uv pip install -r requirements.txt

# Or install from pyproject.toml
uv pip install .
```

4. For development installations (including dev dependencies):
```bash
uv pip install -e ".[dev]"
```

5. To update dependencies to their latest compatible versions:
```bash
uv pip compile requirements.txt --upgrade
```

6. Set up environment variables as described in the standard installation section.

## Usage

Here's a basic example of using the agent to create a new repository:

```python
import asyncio
from pathlib import Path
from agent.repository_agent import RepositoryAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize agent
agent = RepositoryAgent(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-4"
)

# Define your requirements
requirements = {
    "name": "user-service",
    "description": "A REST API microservice for user management",
    "endpoints": [
        {
            "path": "/api/users",
            "method": "GET",
            "description": "List all users with pagination"
        },
        # ... more endpoints ...
    ],
    "domain_entities": [
        {
            "name": "User",
            "attributes": [
                {"name": "id", "type": "str"},
                {"name": "username", "type": "str"},
                {"name": "email", "type": "str"},
                {"name": "created_at", "type": "datetime"}
            ]
        }
    ]
}

# Create repository
async def main():
    success = await agent.create_repository(
        requirements=requirements,
        language="python",
        repo_path=Path("./generated/user-service"),
        remote_url=None  # Optional: Set this for remote repository
    )
    
    if success:
        print("Repository created successfully!")
    else:
        print("Failed to create repository")

if __name__ == "__main__":
    asyncio.run(main())
```

## Project Structure

The project follows a hexagonal architecture pattern:

```
llm-repo-agent/
├── src/
│   ├── core/              # Domain models and business logic
│   ├── application/       # Use cases and application services
│   └── infrastructure/    # External adapters and implementations
├── templates/             # Language-specific project templates
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
└── requirements.txt       # Dependencies
```

## Dependencies

- Python >= 3.9
- langchain >= 0.1.0
- openai >= 1.0.0
- gitpython >= 3.1.0
- python-dotenv >= 1.0.0
- Additional dependencies listed in `pyproject.toml`

## Development

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please open an issue in the repository.
