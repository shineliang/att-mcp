import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode='require'  # Add SSL mode to require secure connection
    )
    return conn

def execute_query(query, params=None, fetch_one=False):
    """Execute a query and return the results"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith(("SELECT", "WITH")):
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.rowcount
    except psycopg2.OperationalError as e:
        # Handle connection errors specifically
        error_msg = f"Database connection error: {str(e)}"
        print(error_msg)  # Log the error
        raise Exception(error_msg) from e
    except Exception as e:
        if conn:
            conn.rollback()
        error_msg = f"Database error: {str(e)}"
        print(error_msg)  # Log the error
        raise Exception(error_msg) from e
    finally:
        if conn:
            conn.close()

def execute_transaction(queries_and_params):
    """Execute multiple queries in a transaction"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            results = []
            for query, params in queries_and_params:
                cursor.execute(query, params)
                if query.strip().upper().startswith(("SELECT", "WITH")):
                    results.append(cursor.fetchall())
                else:
                    results.append(cursor.rowcount)
            conn.commit()
            return results
    except psycopg2.OperationalError as e:
        # Handle connection errors specifically
        error_msg = f"Database connection error: {str(e)}"
        print(error_msg)  # Log the error
        raise Exception(error_msg) from e
    except Exception as e:
        if conn:
            conn.rollback()
        error_msg = f"Database error: {str(e)}"
        print(error_msg)  # Log the error
        raise Exception(error_msg) from e
    finally:
        if conn:
            conn.close()
