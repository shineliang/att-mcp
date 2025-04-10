from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import json
import functools

from mcp.server.fastmcp import FastMCP, Context
import db

# Decorator to handle database errors
def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            print(f"Error in {func.__name__}: {error_message}")
            return f"Error executing {func.__name__}: {error_message}"
    return wrapper

# Create an MCP server
mcp = FastMCP("AttendanceSystem")

# ==================== Employee Information Tools ====================

@mcp.tool()
def get_employee_info(employee_id: int = None, employee_number: str = None) -> str:
    """
    Get employee information by ID or employee number.

    Args:
        employee_id: The ID of the employee (optional if employee_number is provided)
        employee_number: The employee number (optional if employee_id is provided)

    Returns:
        Employee information in a formatted string
    """
    if not employee_id and not employee_number:
        return "Error: Either employee_id or employee_number must be provided"

    query = """
    SELECT * FROM employee_department_view
    WHERE 1=1
    """
    params = []

    if employee_id:
        query += " AND employee_id = %s"
        params.append(employee_id)

    if employee_number:
        query += " AND employee_number = %s"
        params.append(employee_number)

    result = db.execute_query(query, params, fetch_one=True)

    if not result:
        return f"No employee found with the provided information"

    return json.dumps(dict(result), indent=2, default=str)

@mcp.tool()
def list_employees(department_id: Optional[int] = None, status: Optional[str] = None) -> str:
    """
    List employees with optional filtering by department and status.

    Args:
        department_id: Filter by department ID (optional)
        status: Filter by employee status (e.g., 'Active', 'Inactive') (optional)

    Returns:
        List of employees in a formatted string
    """
    query = """
    SELECT employee_id, employee_number, employee_name, position,
           dept_name, hire_date, employee_status
    FROM employee_department_view
    WHERE 1=1
    """
    params = []

    if department_id:
        query += " AND department_id = %s"
        params.append(department_id)

    if status:
        query += " AND employee_status = %s"
        params.append(status)

    query += " ORDER BY dept_name, employee_name"

    results = db.execute_query(query, params)

    if not results:
        return "No employees found with the specified criteria"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

@mcp.tool()
def list_departments() -> str:
    """
    List all departments.

    Returns:
        List of departments in a formatted string
    """
    query = """
    SELECT id, dept_code, dept_name, description,
           parent_id, (SELECT dept_name FROM departments p WHERE p.id = d.parent_id) as parent_name
    FROM departments d
    ORDER BY dept_name
    """

    results = db.execute_query(query)

    if not results:
        return "No departments found"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

# ==================== Attendance Record Tools ====================

@mcp.tool()
def get_attendance_records(
    employee_id: Optional[int] = None,
    employee_number: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    Get attendance records with optional filtering.

    Args:
        employee_id: Filter by employee ID (optional)
        employee_number: Filter by employee number (optional)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        status: Filter by attendance status (e.g., 'Normal', 'Late', 'Absent') (optional)

    Returns:
        Attendance records in a formatted string
    """
    query = """
    SELECT * FROM attendance_detail_view
    WHERE 1=1
    """
    params = []

    if employee_id:
        query += " AND employee_id = %s"
        params.append(employee_id)

    if employee_number:
        query += " AND employee_number = %s"
        params.append(employee_number)

    if start_date:
        query += " AND record_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND record_date <= %s"
        params.append(end_date)

    if status:
        query += " AND attendance_status = %s"
        params.append(status)

    query += " ORDER BY record_date DESC, employee_name"

    results = db.execute_query(query, params)

    if not results:
        return "No attendance records found with the specified criteria"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

@mcp.tool()
def submit_attendance_record(
    employee_id: int,
    record_date: str,
    clock_in_time: Optional[str] = None,
    clock_out_time: Optional[str] = None,
    status: str = "Normal",
    remark: Optional[str] = None
) -> str:
    """
    Submit a new attendance record or update an existing one.

    Args:
        employee_id: The ID of the employee
        record_date: The date of the record in YYYY-MM-DD format
        clock_in_time: Clock-in time in YYYY-MM-DD HH:MM:SS format (optional)
        clock_out_time: Clock-out time in YYYY-MM-DD HH:MM:SS format (optional)
        status: Attendance status (default: 'Normal')
        remark: Additional remarks (optional)

    Returns:
        Result message
    """
    # Check if record already exists
    check_query = """
    SELECT id FROM attendance_records
    WHERE employee_id = %s AND record_date = %s
    """
    existing_record = db.execute_query(check_query, [employee_id, record_date], fetch_one=True)

    if existing_record:
        # Update existing record
        query = """
        UPDATE attendance_records
        SET
            clock_in_time = COALESCE(%s, clock_in_time),
            clock_out_time = COALESCE(%s, clock_out_time),
            status = %s,
            remark = COALESCE(%s, remark),
            updated_at = CURRENT_TIMESTAMP
        WHERE employee_id = %s AND record_date = %s
        RETURNING id
        """
        params = [clock_in_time, clock_out_time, status, remark, employee_id, record_date]
        result = db.execute_query(query, params, fetch_one=True)
        return f"Attendance record updated successfully with ID: {result['id']}"
    else:
        # Insert new record
        query = """
        INSERT INTO attendance_records
        (employee_id, record_date, clock_in_time, clock_out_time, status, remark)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        params = [employee_id, record_date, clock_in_time, clock_out_time, status, remark]
        result = db.execute_query(query, params, fetch_one=True)
        return f"Attendance record created successfully with ID: {result['id']}"

# ==================== Leave Management Tools ====================

@mcp.tool()
def get_leave_requests(
    employee_id: Optional[int] = None,
    employee_number: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    leave_type: Optional[str] = None
) -> str:
    """
    Get leave requests with optional filtering.

    Args:
        employee_id: Filter by employee ID (optional)
        employee_number: Filter by employee number (optional)
        start_date: Filter by leave start date in YYYY-MM-DD format (optional)
        end_date: Filter by leave end date in YYYY-MM-DD format (optional)
        status: Filter by leave status (e.g., 'Pending', 'Approved', 'Rejected') (optional)
        leave_type: Filter by leave type (e.g., 'Annual', 'Sick', 'Personal') (optional)

    Returns:
        Leave requests in a formatted string
    """
    query = """
    SELECT * FROM leave_detail_view
    WHERE 1=1
    """
    params = []

    if employee_id:
        query += " AND employee_id = %s"
        params.append(employee_id)

    if employee_number:
        query += " AND employee_number = %s"
        params.append(employee_number)

    if start_date:
        query += " AND start_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND end_date <= %s"
        params.append(end_date)

    if status:
        query += " AND leave_status = %s"
        params.append(status)

    if leave_type:
        query += " AND leave_type = %s"
        params.append(leave_type)

    query += " ORDER BY start_date DESC, employee_name"

    results = db.execute_query(query, params)

    if not results:
        return "No leave requests found with the specified criteria"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

@mcp.tool()
def submit_leave_request(
    employee_id: int,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str,
    duration: Optional[float] = None
) -> str:
    """
    Submit a new leave request.

    Args:
        employee_id: The ID of the employee
        leave_type: Type of leave (e.g., 'Annual', 'Sick', 'Personal')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        reason: Reason for the leave
        duration: Duration in days (optional, will be calculated if not provided)

    Returns:
        Result message
    """
    # Calculate duration if not provided
    if not duration:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        duration = (end - start).days + 1

    query = """
    INSERT INTO leaves
    (employee_id, leave_type, start_date, end_date, duration, reason, status)
    VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
    RETURNING id
    """
    params = [employee_id, leave_type, start_date, end_date, duration, reason]
    result = db.execute_query(query, params, fetch_one=True)

    return f"Leave request submitted successfully with ID: {result['id']}"

@mcp.tool()
def approve_leave_request(
    leave_id: int,
    approved_by: int,
    status: str = "Approved"
) -> str:
    """
    Approve or reject a leave request.

    Args:
        leave_id: The ID of the leave request
        approved_by: The ID of the approver
        status: New status ('Approved' or 'Rejected')

    Returns:
        Result message
    """
    if status not in ["Approved", "Rejected"]:
        return "Error: Status must be either 'Approved' or 'Rejected'"

    query = """
    UPDATE leaves
    SET status = %s, approved_by = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id
    """
    params = [status, approved_by, leave_id]
    result = db.execute_query(query, params, fetch_one=True)

    if not result:
        return f"Error: Leave request with ID {leave_id} not found"

    return f"Leave request {status.lower()} successfully"

# ==================== Overtime Management Tools ====================

@mcp.tool()
def get_overtime_requests(
    employee_id: Optional[int] = None,
    employee_number: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    Get overtime requests with optional filtering.

    Args:
        employee_id: Filter by employee ID (optional)
        employee_number: Filter by employee number (optional)
        start_date: Filter by overtime date in YYYY-MM-DD format (optional)
        end_date: Filter by overtime date in YYYY-MM-DD format (optional)
        status: Filter by overtime status (e.g., 'Pending', 'Approved', 'Rejected') (optional)

    Returns:
        Overtime requests in a formatted string
    """
    query = """
    SELECT * FROM overtime_detail_view
    WHERE 1=1
    """
    params = []

    if employee_id:
        query += " AND employee_id = %s"
        params.append(employee_id)

    if employee_number:
        query += " AND employee_number = %s"
        params.append(employee_number)

    if start_date:
        query += " AND overtime_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND overtime_date <= %s"
        params.append(end_date)

    if status:
        query += " AND overtime_status = %s"
        params.append(status)

    query += " ORDER BY overtime_date DESC, employee_name"

    results = db.execute_query(query, params)

    if not results:
        return "No overtime requests found with the specified criteria"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

@mcp.tool()
def submit_overtime_request(
    employee_id: int,
    overtime_date: str,
    start_time: str,
    end_time: str,
    reason: str
) -> str:
    """
    Submit a new overtime request.

    Args:
        employee_id: The ID of the employee
        overtime_date: Date of overtime in YYYY-MM-DD format
        start_time: Start time in YYYY-MM-DD HH:MM:SS format
        end_time: End time in YYYY-MM-DD HH:MM:SS format
        reason: Reason for the overtime

    Returns:
        Result message
    """
    # Calculate hours
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    hours = (end - start).total_seconds() / 3600

    query = """
    INSERT INTO overtimes
    (employee_id, overtime_date, start_time, end_time, hours, reason, status)
    VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
    RETURNING id
    """
    params = [employee_id, overtime_date, start_time, end_time, hours, reason]
    result = db.execute_query(query, params, fetch_one=True)

    return f"Overtime request submitted successfully with ID: {result['id']}"

@mcp.tool()
def approve_overtime_request(
    overtime_id: int,
    approved_by: int,
    status: str = "Approved"
) -> str:
    """
    Approve or reject an overtime request.

    Args:
        overtime_id: The ID of the overtime request
        approved_by: The ID of the approver
        status: New status ('Approved' or 'Rejected')

    Returns:
        Result message
    """
    if status not in ["Approved", "Rejected"]:
        return "Error: Status must be either 'Approved' or 'Rejected'"

    query = """
    UPDATE overtimes
    SET status = %s, approved_by = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id
    """
    params = [status, approved_by, overtime_id]
    result = db.execute_query(query, params, fetch_one=True)

    if not result:
        return f"Error: Overtime request with ID {overtime_id} not found"

    return f"Overtime request {status.lower()} successfully"

# ==================== Schedule Management Tools ====================

@mcp.tool()
def get_employee_schedule(
    employee_id: Optional[int] = None,
    employee_number: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Get employee schedule with optional filtering.

    Args:
        employee_id: Filter by employee ID (optional if employee_number is provided)
        employee_number: Filter by employee number (optional if employee_id is provided)
        start_date: Filter by schedule start date in YYYY-MM-DD format (optional)
        end_date: Filter by schedule end date in YYYY-MM-DD format (optional)

    Returns:
        Employee schedule in a formatted string
    """
    if not employee_id and not employee_number:
        return "Error: Either employee_id or employee_number must be provided"

    query = """
    SELECT s.id as schedule_id, e.id as employee_id, e.employee_number, e.name as employee_name,
           s.start_date, s.end_date, sh.id as shift_id, sh.shift_name,
           sh.start_time, sh.end_time, sh.is_night_shift
    FROM schedules s
    JOIN employees e ON s.employee_id = e.id
    JOIN shifts sh ON s.shift_id = sh.id
    WHERE 1=1
    """
    params = []

    if employee_id:
        query += " AND e.id = %s"
        params.append(employee_id)

    if employee_number:
        query += " AND e.employee_number = %s"
        params.append(employee_number)

    if start_date:
        query += " AND s.start_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND s.end_date <= %s"
        params.append(end_date)

    query += " ORDER BY s.start_date, e.name"

    results = db.execute_query(query, params)

    if not results:
        return "No schedules found with the specified criteria"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

@mcp.tool()
def list_shifts() -> str:
    """
    List all available shifts.

    Returns:
        List of shifts in a formatted string
    """
    query = """
    SELECT id, shift_name, start_time, end_time, is_night_shift
    FROM shifts
    ORDER BY start_time
    """

    results = db.execute_query(query)

    if not results:
        return "No shifts found"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

@mcp.tool()
def assign_schedule(
    employee_id: int,
    shift_id: int,
    start_date: str,
    end_date: str
) -> str:
    """
    Assign a schedule to an employee.

    Args:
        employee_id: The ID of the employee
        shift_id: The ID of the shift
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Result message
    """
    # Check for overlapping schedules
    check_query = """
    SELECT id FROM schedules
    WHERE employee_id = %s
    AND (
        (start_date <= %s AND end_date >= %s) OR
        (start_date <= %s AND end_date >= %s) OR
        (start_date >= %s AND end_date <= %s)
    )
    """
    params = [employee_id, start_date, start_date, end_date, end_date, start_date, end_date]
    existing_schedule = db.execute_query(check_query, params, fetch_one=True)

    if existing_schedule:
        return f"Error: Employee already has a schedule that overlaps with the specified date range"

    query = """
    INSERT INTO schedules
    (employee_id, shift_id, start_date, end_date)
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """
    params = [employee_id, shift_id, start_date, end_date]
    result = db.execute_query(query, params, fetch_one=True)

    return f"Schedule assigned successfully with ID: {result['id']}"

# ==================== Statistics and Reports ====================

@mcp.tool()
def get_monthly_attendance_stats(
    year: int,
    month: int,
    department_id: Optional[int] = None,
    employee_id: Optional[int] = None
) -> str:
    """
    Get monthly attendance statistics.

    Args:
        year: The year
        month: The month (1-12)
        department_id: Filter by department ID (optional)
        employee_id: Filter by employee ID (optional)

    Returns:
        Monthly attendance statistics in a formatted string
    """
    query = """
    SELECT * FROM monthly_attendance_stats
    WHERE year = %s AND month = %s
    """
    params = [year, month]

    if department_id:
        # Join with employees to filter by department
        query = """
        SELECT mas.* FROM monthly_attendance_stats mas
        JOIN employees e ON mas.employee_id = e.id
        WHERE mas.year = %s AND mas.month = %s AND e.department_id = %s
        """
        params = [year, month, department_id]

    if employee_id:
        query += " AND employee_id = %s"
        params.append(employee_id)

    query += " ORDER BY dept_name, employee_name"

    results = db.execute_query(query, params)

    if not results:
        return "No attendance statistics found for the specified criteria"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

@mcp.tool()
def get_holidays(
    year: Optional[int] = None,
    month: Optional[int] = None,
    is_paid: Optional[bool] = None
) -> str:
    """
    Get holidays with optional filtering.

    Args:
        year: Filter by year (optional)
        month: Filter by month (1-12) (optional)
        is_paid: Filter by paid status (optional)

    Returns:
        Holidays in a formatted string
    """
    query = """
    SELECT id, holiday_name, holiday_date, is_paid
    FROM holidays
    WHERE 1=1
    """
    params = []

    if year:
        query += " AND EXTRACT(YEAR FROM holiday_date) = %s"
        params.append(year)

    if month:
        query += " AND EXTRACT(MONTH FROM holiday_date) = %s"
        params.append(month)

    if is_paid is not None:
        query += " AND is_paid = %s"
        params.append(is_paid)

    query += " ORDER BY holiday_date"

    results = db.execute_query(query, params)

    if not results:
        return "No holidays found with the specified criteria"

    return json.dumps([dict(r) for r in results], indent=2, default=str)

# ==================== Resources ====================

@mcp.resource("employee://{employee_id}")
def get_employee_resource(employee_id: int) -> str:
    """
    Get employee information as a resource.

    Args:
        employee_id: The ID of the employee

    Returns:
        Employee information in a formatted string
    """
    query = """
    SELECT * FROM employee_department_view
    WHERE employee_id = %s
    """
    result = db.execute_query(query, [employee_id], fetch_one=True)

    if not result:
        return f"No employee found with ID: {employee_id}"

    return json.dumps(dict(result), indent=2, default=str)

@mcp.resource("department://{department_id}")
def get_department_resource(department_id: int) -> str:
    """
    Get department information as a resource.

    Args:
        department_id: The ID of the department

    Returns:
        Department information in a formatted string
    """
    query = """
    SELECT d.*,
           (SELECT dept_name FROM departments p WHERE p.id = d.parent_id) as parent_name,
           (SELECT COUNT(*) FROM employees e WHERE e.department_id = d.id) as employee_count
    FROM departments d
    WHERE d.id = %s
    """
    result = db.execute_query(query, [department_id], fetch_one=True)

    if not result:
        return f"No department found with ID: {department_id}"

    return json.dumps(dict(result), indent=2, default=str)

@mcp.resource("attendance://{employee_id}/{date}")
def get_attendance_resource(employee_id: int, date: str) -> str:
    """
    Get attendance information for a specific employee and date.

    Args:
        employee_id: The ID of the employee
        date: The date in YYYY-MM-DD format

    Returns:
        Attendance information in a formatted string
    """
    query = """
    SELECT * FROM attendance_detail_view
    WHERE employee_id = %s AND record_date = %s
    """
    result = db.execute_query(query, [employee_id, date], fetch_one=True)

    if not result:
        return f"No attendance record found for employee ID {employee_id} on {date}"

    return json.dumps(dict(result), indent=2, default=str)

# ==================== Prompts ====================

@mcp.prompt()
def request_leave() -> str:
    """Create a leave request prompt"""
    return """
    I'd like to request leave. Please help me fill out the following information:

    1. Employee ID or Employee Number
    2. Leave Type (Annual, Sick, Personal, etc.)
    3. Start Date (YYYY-MM-DD)
    4. End Date (YYYY-MM-DD)
    5. Reason for leave

    Once you have this information, you can use the submit_leave_request tool to submit my request.
    """

@mcp.prompt()
def request_overtime() -> str:
    """Create an overtime request prompt"""
    return """
    I'd like to request overtime. Please help me fill out the following information:

    1. Employee ID or Employee Number
    2. Overtime Date (YYYY-MM-DD)
    3. Start Time (YYYY-MM-DD HH:MM:SS)
    4. End Time (YYYY-MM-DD HH:MM:SS)
    5. Reason for overtime

    Once you have this information, you can use the submit_overtime_request tool to submit my request.
    """

@mcp.prompt()
def check_attendance() -> str:
    """Create an attendance check prompt"""
    return """
    I'd like to check my attendance records. Please help me by asking for the following information:

    1. Employee ID or Employee Number
    2. Start Date (YYYY-MM-DD) (optional)
    3. End Date (YYYY-MM-DD) (optional)

    Once you have this information, you can use the get_attendance_records tool to retrieve my attendance records.
    """

# Run the server
if __name__ == "__main__":
    mcp.run(transport='stdio')
