# Attendance Management MCP Server

This is a Model Context Protocol (MCP) server for attendance information queries and form applications. It provides tools and resources for managing employee attendance, leave requests, overtime requests, and schedules.

## Features

- Employee information management
- Attendance record tracking
- Leave request management
- Overtime request management
- Schedule management
- Statistics and reports

## Prerequisites

- Python 3.10 or higher
- Neon PostgreSQL database

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/attendance-mcp-server.git
   cd attendance-mcp-server
   ```

2. Set up a virtual environment and install the required dependencies:
   ```
   ./setup_venv.sh
   ```

3. Configure the database connection by creating a `.env` file with the following content:
   ```
   DB_HOST=db.weathered-shadow-70756968.us-east-2.aws.neon.tech
   DB_NAME=shinedb
   DB_USER=shine_user
   DB_PASSWORD=Shine@123456#!
   DB_PORT=5432
   ```

## Running the Server

You can run the server using the wrapper script:

```
./run_mcp.sh
```

Or activate the virtual environment and use the MCP CLI:

```
source .venv/bin/activate
mcp run attendance_mcp_server.py
```

## Using with Claude Desktop

To use this server with Claude Desktop:

1. Install Claude Desktop from [claude.ai/download](https://claude.ai/download)

2. Run the installation script to configure Claude Desktop:
   ```
   python install_claude_desktop.py
   ```

3. Restart Claude Desktop

### Troubleshooting

If you encounter the "No module named 'mcp'" error:

1. Make sure the MCP package is installed in the Python environment that Claude Desktop is using:
   ```
   ./install_dependencies.sh
   ```

2. Check the Claude Desktop logs for more information:
   - On macOS: `~/Library/Logs/Claude/mcp*.log`
   - On Windows: `%APPDATA%\Claude\Logs\mcp*.log`

3. If the issue persists, try running the MCP server manually to see if there are any errors:
   ```
   ./run_attendance_mcp.sh
   ```

## Available Tools

### Employee Information
- `get_employee_info`: Get employee information by ID or employee number
- `list_employees`: List employees with optional filtering
- `list_departments`: List all departments

### Attendance Records
- `get_attendance_records`: Get attendance records with optional filtering
- `submit_attendance_record`: Submit a new attendance record or update an existing one

### Leave Management
- `get_leave_requests`: Get leave requests with optional filtering
- `submit_leave_request`: Submit a new leave request
- `approve_leave_request`: Approve or reject a leave request

### Overtime Management
- `get_overtime_requests`: Get overtime requests with optional filtering
- `submit_overtime_request`: Submit a new overtime request
- `approve_overtime_request`: Approve or reject an overtime request

### Schedule Management
- `get_employee_schedule`: Get employee schedule with optional filtering
- `list_shifts`: List all available shifts
- `assign_schedule`: Assign a schedule to an employee

### Statistics and Reports
- `get_monthly_attendance_stats`: Get monthly attendance statistics
- `get_holidays`: Get holidays with optional filtering

## Available Resources

- `employee://{employee_id}`: Get employee information as a resource
- `department://{department_id}`: Get department information as a resource
- `attendance://{employee_id}/{date}`: Get attendance information for a specific employee and date

## Available Prompts

- `request_leave`: Create a leave request prompt
- `request_overtime`: Create an overtime request prompt
- `check_attendance`: Create an attendance check prompt

## License

MIT
