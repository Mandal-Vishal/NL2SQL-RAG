import re

from schema_inspector import get_schema


def clean_sql(sql):
    """
    Remove Markdown code fences if the LLM returns SQL inside them.
    """

    sql = sql.strip()

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

    return sql.strip()


def validate_sql(sql):

    sql = clean_sql(sql)

    # --------------------------------------------------
    # 1. Check whether the query is a SELECT statement
    # --------------------------------------------------

    if not sql.upper().startswith("SELECT"):

        return False, "Only SELECT queries are allowed."


    # --------------------------------------------------
    # 2. Block dangerous SQL operations
    # --------------------------------------------------

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

            return (
                False,
                f"Dangerous SQL operation detected: {keyword}"
            )


    # --------------------------------------------------
    # 3. Get actual database schema
    # --------------------------------------------------

    schema = get_schema()


    # --------------------------------------------------
    # 4. Check table names
    # --------------------------------------------------

    valid_tables = {
        table_name.lower()
        for table_name in schema.keys()
    }


    # Find tables after FROM and JOIN
    table_matches = re.findall(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        flags=re.IGNORECASE
    )


    for table in table_matches:

        if table.lower() not in valid_tables:

            return (
                False,
                f"Table does not exist: {table}"
            )


    # --------------------------------------------------
    # 5. Check qualified column names
    # --------------------------------------------------

    valid_columns = {}

    for table_name, table_data in schema.items():

        valid_columns[table_name.lower()] = {
            column["name"].lower()
            for column in table_data["columns"]
        }


    # Find expressions like:
    # customers.customer_id
    # bookings.car_id
    # cars.brand

    qualified_columns = re.findall(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b",
        sql
    )


    # Map aliases to actual table names

    aliases = {}

    alias_matches = re.findall(
        r"\b(?:FROM|JOIN)\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*)"
        r"(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?",
        sql,
        flags=re.IGNORECASE
    )


    for table_name, alias in alias_matches:

        if alias:

            aliases[alias.lower()] = table_name.lower()

        else:

            aliases[table_name.lower()] = table_name.lower()


    # Check each qualified column

    for table_reference, column_name in qualified_columns:

        table_reference = table_reference.lower()
        column_name = column_name.lower()

        actual_table = aliases.get(
            table_reference,
            table_reference
        )


        # Skip unknown references for now
        # They will be handled by MySQL later.

        if actual_table not in valid_columns:

            continue


        if column_name not in valid_columns[actual_table]:

            return (
                False,
                f"Column '{column_name}' does not exist "
                f"in table '{actual_table}'."
            )


    return True, "SQL passed schema validation."


if __name__ == "__main__":

    test_sql = """
SELECT customers.customer_name
FROM customers;
"""

    is_valid, message = validate_sql(test_sql)

    print("Valid:", is_valid)
    print("Message:", message)