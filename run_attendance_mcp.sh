#!/bin/bash

# Enable verbose output
set -x

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script directory: $DIR"

# Check if virtual environment exists, if not create it
if [ ! -d "$DIR/.venv" ]; then
    echo "Virtual environment not found. Setting up..."
    "$DIR/setup_venv.sh"
fi

# Activate the virtual environment
source "$DIR/.venv/bin/activate"

# Check Python version
python --version

# List installed packages
pip list | grep -E "mcp|psycopg2|dotenv"

# Run the MCP server
echo "Starting MCP server..."
mcp run "$DIR/attendance_mcp_server.py"
