#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$DIR/.venv/bin/activate"

# Run the MCP server
mcp run "$DIR/attendance_mcp_server.py"
