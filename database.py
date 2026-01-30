"""
Database operations for Local Lens application.
All SQLite database functions are centralized here.
"""
import sqlite3
import pandas as pd
from config import DATABASE_PATH


def create_database():
    """Create SQLite database and reports table if they don't exist"""
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        # Create the reports table with enhanced schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                additional_details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Reported',
                priority TEXT DEFAULT 'Medium'
            )
        ''')
        
        # Check if new columns exist, add them if not (for backwards compatibility)
        cursor.execute("PRAGMA table_info(reports)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN status TEXT DEFAULT 'Reported'")
        
        if 'priority' not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN priority TEXT DEFAULT 'Medium'")
        
        if 'additional_details' not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN additional_details TEXT")
        
        if 'email' not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN email TEXT")
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def insert_report(image_path, category, location, additional_details=None, email=None):
    """Insert a new record into the reports table
    
    Args:
        image_path (str): Path to the saved image file
        category (str): Issue category
        location (str): Location description
        additional_details (str, optional): Additional information about the issue
        email (str, optional): Contact email for follow-up
        
    Returns:
        int: Report ID if successful, None otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO reports (image_path, category, location, additional_details, email) 
               VALUES (?, ?, ?, ?, ?)''',
            (image_path, category, location, additional_details, email)
        )
        conn.commit()
        return cursor.lastrowid
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def get_all_reports():
    """Retrieve all reports from the database
    
    Returns:
        list: List of all report records
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY timestamp DESC")
        return cursor.fetchall()
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()


def get_recent_reports(limit: int = 5):
    """Retrieve the most recent reports limited by count
    
    Args:
        limit (int): Number of most recent reports to return
    Returns:
        list: List of recent report records
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY timestamp DESC LIMIT ?", (limit,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_filtered_reports(category=None, status=None, date_from=None, date_to=None, location=None):
    """Get reports with optional filters
    
    Args:
        category (str, optional): Filter by category
        status (str, optional): Filter by status
        date_from (datetime, optional): Filter by start date
        date_to (datetime, optional): Filter by end date
        location (str, optional): Filter by location (partial match)
    
    Returns:
        list: Filtered report records
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        query = "SELECT * FROM reports WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if date_from:
            query += " AND DATE(timestamp) >= ?"
            params.append(str(date_from))
        
        if date_to:
            query += " AND DATE(timestamp) <= ?"
            params.append(str(date_to))
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()


def update_report_status(report_id, status):
    """Update the status of a report
    
    Args:
        report_id (int): ID of the report to update
        status (str): New status value
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def update_report_priority(report_id, priority):
    """Update the priority of a report
    
    Args:
        report_id (int): ID of the report to update
        priority (str): New priority value
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("UPDATE reports SET priority = ? WHERE id = ?", (priority, report_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def update_report(report_id, category, location, additional_details):
    """Update report details
    
    Args:
        report_id (int): ID of the report to update
        category (str): New category
        location (str): New location
        additional_details (str): New additional details
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE reports SET category = ?, location = ?, additional_details = ? WHERE id = ?",
            (category, location, additional_details, report_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def delete_report(report_id):
    """Delete a report from the database
    
    Args:
        report_id (int): ID of the report to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_report_by_id(report_id):
    """Get a single report by ID
    
    Args:
        report_id (int): ID of the report
    
    Returns:
        tuple: Report record or None
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_report_statistics():
    """Get statistics about submitted reports
    
    Returns:
        dict: Dictionary with statistics (total_count, category_counts)
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_count = cursor.fetchone()[0]
        
        # Get counts by category
        cursor.execute("SELECT category, COUNT(*) FROM reports GROUP BY category")
        category_counts = dict(cursor.fetchall())
        
        return {
            'total_count': total_count,
            'category_counts': category_counts
        }
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {'total_count': 0, 'category_counts': {}}
    
    finally:
        if conn:
            conn.close()


def export_reports_to_csv():
    """Export all reports to CSV format
    
    Returns:
        str: CSV data as string
    """
    reports = get_all_reports()
    if not reports:
        return None
    
    # Create DataFrame - handle both old (8 cols) and new (9 cols with email) records
    if reports and len(reports[0]) >= 9:
        df = pd.DataFrame(reports, columns=[
            'ID', 'Image Path', 'Category', 'Location', 
            'Additional Details', 'Timestamp', 'Status', 'Priority', 'Email'
        ])
    else:
        df = pd.DataFrame(reports, columns=[
            'ID', 'Image Path', 'Category', 'Location', 
            'Additional Details', 'Timestamp', 'Status', 'Priority'
        ])
    return df.to_csv(index=False)
