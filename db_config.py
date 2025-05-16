import mysql.connector
import boto3
import json

def get_db_secret():
    secret_name = "prod/rds/mysql"
    region_name = "us-west-2"  # e.g., "ap-south-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret

def get_connection():
    secret = get_db_secret()
    return mysql.connector.connect(
        host=secret['host'],
        user=secret['username'],
        password=secret['password'],
        database=secret['dbname']
    )
