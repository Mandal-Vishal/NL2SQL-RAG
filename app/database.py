import mysql.connector
import os

from dotenv import load_dotenv


load_dotenv()


def get_connection():

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    return connection


def execute_sql(sql):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(sql)

    results = cursor.fetchall()

    columns = cursor.column_names

    cursor.close()

    connection.close()

    return columns, results

if __name__ == "__main__":

    test_sql = """
    SELECT name, city
    FROM Customers
    WHERE city = 'Mumbai';
    """

    columns, results = execute_sql(test_sql)

    print("Columns:")
    print(columns)

    print("\nResults:")

    for row in results:
        print(row)