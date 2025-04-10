import subprocess
import sys

def run_test():
    """Test the MCP server using the MCP CLI"""
    print("Testing the Attendance MCP Server...")

    # Run the MCP server in dev mode
    print("\nStarting the MCP server in dev mode...")
    print("Please open the MCP Inspector at http://127.0.0.1:6274 to interact with the server.")
    print("Press Ctrl+C to stop the server when done.")

    try:
        subprocess.run(["mcp", "dev", "attendance_mcp_server.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"\nError running the MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
