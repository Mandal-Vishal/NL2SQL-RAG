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

    cleaned_columns = []

    for column in columns:
        column_name = column[0]
        data_type = column[1]
        key = column[3]

        clean_column = {
            'name' : column_name,
            'type':data_type,
            'key':key
        }

        cleaned_columns.append(clean_column)

    cursor.close()
    connection.close()

    return cleaned_columns

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

    cleaned_foreign_keys = []

    for foreign_key in foreign_keys:
        column_name = foreign_key[0]
        reference_table = foreign_key[1]
        reference_column = foreign_key[2]

        clean_foreign_key  = {
            'column':column_name,
            'references':f'{reference_table}.{reference_column}'
        }

        cleaned_foreign_keys.append(clean_foreign_key)

    cursor.close()
    connection.close()

    return cleaned_foreign_keys

#Function to respresent schema
def get_schema():
    tables = get_tables()

    schema = {}

    for table in tables:
        table_name  = table[0]

        columns = get_columns(table_name)
        foreign_keys = get_foreign_keys(table_name)

        schema[table_name] = {
            'columns':columns,
            'foreign_keys':foreign_keys
        }

    return schema


#For testing
if __name__ == '__main__':
   schema = get_schema()

   for table_name , table_data in schema.items():
       print('\nTable :' , table_name)

       print('columns :')
       for column in table_data['columns']:
           print(column)

       print('Foreign_Keys : ')
       for foreign_key in table_data['foreign_keys']:
           print(foreign_key)