#!/usr/bin/env python

import sys
import subprocess

def check_mcp_installation():
    """Check if the MCP package is installed correctly"""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    try:
        import mcp
        print(f"MCP package found: {mcp.__version__}")
        print(f"MCP package location: {mcp.__file__}")
    except ImportError:
        print("MCP package not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "mcp[cli]>=1.6.0"], check=True)
            import mcp
            print(f"MCP package installed: {mcp.__version__}")
        except Exception as e:
            print(f"Error installing MCP package: {e}")
            return False
    
    try:
        import psycopg2
        print(f"psycopg2 package found: {psycopg2.__version__}")
    except ImportError:
        print("psycopg2 package not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary>=2.9.9"], check=True)
        except Exception as e:
            print(f"Error installing psycopg2 package: {e}")
            return False
    
    try:
        import dotenv
        print(f"python-dotenv package found: {dotenv.__version__}")
    except ImportError:
        print("python-dotenv package not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv>=1.0.0"], check=True)
        except Exception as e:
            print(f"Error installing python-dotenv package: {e}")
            return False
    
    print("\nAll required packages are installed correctly.")
    return True

if __name__ == "__main__":
    if check_mcp_installation():
        print("\nYou can now run the MCP server with:")
        print("  mcp run attendance_mcp_server.py")
    else:
        print("\nThere was an error installing the required packages.")
        print("Please check the error messages above and try again.")
