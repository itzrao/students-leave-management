import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="db-nielit.cl6muqgg8bt3.ap-south-1.rds.amazonaws.com",
        user="admin",
        password="Sai909868",  # Add your MySQL password here
        database="leave_system"
    )
