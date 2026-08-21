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

#function to find tables in a database
def get_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('show tables')

    tables = cursor.fetchall()

    cursor.close()
    connection.close()

    return tables

#function to find columns in a table
def get_columns(table_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(f"describe {table_name}")

    columns = cursor.fetchall()

    cursor.close()
    connection.close()

    return columns

#function to find foreign-key relationships of any table
def get_foreign_keys(table_name):#
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    select column_name , referenced_table_name , referenced_column_name
    from information_schema.key_column_usage
    where table_schema = %s
    and table_name = %s
    and referenced_table_name is not null
    """

    cursor.execute(query , (os.getenv('MYSQL_DATABASE') , table_name))

    foreign_keys = cursor.fetchall()

    cursor.close()
    connection.close()

    return foreign_keys

#For testing
if __name__ == '__main__':
    foreign_keys = get_foreign_keys("bookings")
    for foreign_key in foreign_keys:
        print(foreign_key)