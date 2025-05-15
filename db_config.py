import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",  # Add your MySQL password here
        database="student_leave_system"
    )
