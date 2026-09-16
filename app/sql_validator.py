import re


def validate_sql(sql):

    sql = sql.strip()

    # Remove markdown code fences if Gemini returns them
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    sql = sql.strip()

    # Only allow SELECT queries
    if not sql.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    # Block dangerous SQL operations
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

        if re.search(rf"\b{keyword}\b", upper_sql):
            return False, f"Dangerous SQL operation detected: {keyword}"

    return True, "SQL passed basic validation."


if __name__ == "__main__":

    test_sql = """
    SELECT DISTINCT customers.customer_id, customers.name
    FROM customers
    JOIN bookings
        ON customers.customer_id = bookings.customer_id
    JOIN cars
        ON bookings.car_id = cars.car_id
    WHERE cars.brand = 'Honda';
    """

    is_valid, message = validate_sql(test_sql)

    print("Valid:", is_valid)
    print("Message:", message)