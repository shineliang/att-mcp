import os
import json
import platform
import sys
from pathlib import Path

def get_config_path():
    """Get the path to the Claude Desktop config file based on the platform"""
    if platform.system() == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
    elif platform.system() == "Windows":
        return os.path.join(os.environ["APPDATA"], "Claude", "claude_desktop_config.json")
    else:
        print("Unsupported platform. Only macOS and Windows are supported.")
        sys.exit(1)

def install_mcp_server():
    """Install the attendance MCP server in Claude Desktop"""
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)

    # Create the config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Get the absolute path to the MCP server script
    server_path = os.path.abspath("attendance_mcp_server.py")

    # Load existing config or create a new one
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}

    # Ensure mcpServers key exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Get the absolute path to the wrapper script
    wrapper_path = os.path.abspath("run_mcp.sh")

    # Add our server to the config
    config["mcpServers"]["attendance"] = {
        "command": wrapper_path,
        "args": []
    }

    # Save the updated config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Attendance MCP server installed successfully in Claude Desktop.")
    print(f"Configuration saved to: {config_path}")
    print("Please restart Claude Desktop to apply the changes.")

if __name__ == "__main__":
    install_mcp_server()
