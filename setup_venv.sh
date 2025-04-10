#!/bin/bash

# Create a virtual environment for the MCP server
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the required packages
pip install "mcp[cli]>=1.6.0" psycopg2-binary>=2.9.9 python-dotenv>=1.0.0

# Verify the installation
python -c "import mcp; print(f'MCP version: {mcp.__version__}')"

echo "Virtual environment setup complete. To activate it, run:"
echo "source .venv/bin/activate"
