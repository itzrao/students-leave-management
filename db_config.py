import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="xxxxx.ap-south-1.rds.amazonaws.com",
        user="xxxx",
        password="xxxxx",  # Add your MySQL password here
        database="leave_system"
    )
