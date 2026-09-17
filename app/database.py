import mysql.connector
import os
import re

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


def is_read_only_sql(sql):

    sql = sql.strip()

    # Remove Markdown code fences
    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```",
        "",
        sql
    )

    sql = sql.strip()

    # Only SELECT queries are allowed
    if not sql.upper().startswith("SELECT"):

        return False

    # Dangerous operations
    dangerous_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "RENAME"
    ]

    upper_sql = sql.upper()

    for keyword in dangerous_keywords:

        if re.search(
            rf"\b{keyword}\b",
            upper_sql
        ):

            return False

    return True


def execute_sql(sql):

    # Read-only safety gate
    if not is_read_only_sql(sql):

        raise ValueError(
            "Unsafe SQL blocked. "
            "Only SELECT queries are allowed."
        )

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