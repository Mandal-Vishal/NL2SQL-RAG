import os 
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
    host  = os.getenv('MYSQL_HOST'),
    user = os.getenv('MYSQL_USER'),
    password = os.getenv('MYSQL_PASSWORD'),
    database = os.getenv('MYSQL_DATABASE')
)

def get_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('show tables')

    tables = cursor.fetchall()

    cursor.close()
    connection.close()

    return tables

if __name__ == '__main__':
    tables = get_tables()

    for table in tables:
        print(table[0])