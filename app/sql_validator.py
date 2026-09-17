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

    # ---------------------------------------
    # 1. Only allow SELECT queries
    # ---------------------------------------

    if not sql.upper().startswith("SELECT"):

        return False, "Only SELECT queries are allowed."


    # ---------------------------------------
    # 2. Block dangerous SQL operations
    # ---------------------------------------

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


    # ---------------------------------------
    # 3. Get actual database schema
    # ---------------------------------------

    schema = get_schema()


    # ---------------------------------------
    # 4. Create table lookup
    # ---------------------------------------

    valid_tables = {
        table_name.lower()
        for table_name in schema.keys()
    }


    # ---------------------------------------
    # 5. Find tables used by the SQL
    # ---------------------------------------

    table_matches = re.findall(
        r"\b(?:FROM|JOIN)\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        flags=re.IGNORECASE
    )


    used_tables = set()


    for table in table_matches:

        table_lower = table.lower()

        if table_lower not in valid_tables:

            return (
                False,
                f"Table does not exist: {table}"
            )

        used_tables.add(table_lower)


    # ---------------------------------------
    # 6. Build column information
    # ---------------------------------------

    valid_columns = {}

    for table_name, table_data in schema.items():

        valid_columns[table_name.lower()] = {
            column["name"].lower()
            for column in table_data["columns"]
        }


    # ---------------------------------------
    # 7. Build alias → table mapping
    # ---------------------------------------

    aliases = {}

    alias_matches = re.findall(
        r"\b(?:FROM|JOIN)\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*)"
        r"(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?",
        sql,
        flags=re.IGNORECASE
    )


    for table_name, alias in alias_matches:

        table_lower = table_name.lower()

        if alias:

            aliases[alias.lower()] = table_lower

        else:

            aliases[table_lower] = table_lower


    # ---------------------------------------
    # 8. Check qualified columns
    # ---------------------------------------

    qualified_columns = re.findall(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\."
        r"([a-zA-Z_][a-zA-Z0-9_]*)\b",
        sql
    )


    for table_reference, column_name in qualified_columns:

        table_reference = table_reference.lower()
        column_name = column_name.lower()

        actual_table = aliases.get(
            table_reference,
            table_reference
        )


        if actual_table not in valid_columns:

            continue


        if column_name not in valid_columns[actual_table]:

            return (
                False,
                f"Column '{column_name}' does not exist "
                f"in table '{actual_table}'."
            )


    # ---------------------------------------
    # 9. Check unqualified columns
    # ---------------------------------------

    available_columns = set()

    for table in used_tables:

        available_columns.update(
            valid_columns[table]
        )


    # SQL words that are NOT column names
    sql_keywords = {
        "SELECT",
        "FROM",
        "WHERE",
        "JOIN",
        "ON",
        "AS",
        "AND",
        "OR",
        "NOT",
        "NULL",
        "IS",
        "IN",
        "LIKE",
        "BETWEEN",
        "GROUP",
        "BY",
        "ORDER",
        "HAVING",
        "LIMIT",
        "DISTINCT",
        "ASC",
        "DESC",
        "INNER",
        "LEFT",
        "RIGHT",
        "OUTER",
        "FULL",
        "CROSS",
        "UNION",
        "ALL",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END"
    }


    # Common SQL functions
    sql_functions = {
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
        "COALESCE",
        "ROUND",
        "CONCAT"
    }


    # Remove qualified references from consideration
    qualified_column_names = {
        column.lower()
        for _, column in qualified_columns
    }


    # ---------------------------------------
    # Remove string literals
    # ---------------------------------------

    sql_without_strings = re.sub(
        r"'(?:''|[^'])*'",
        "''",
        sql
    )


    # ---------------------------------------
    # Find identifiers
    # ---------------------------------------

    identifiers = re.findall(
        r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
        sql_without_strings
    )


    for identifier in identifiers:

        identifier_lower = identifier.lower()

        # Skip SQL keywords
        if identifier.upper() in sql_keywords:
            continue

        # Skip SQL functions
        if identifier.upper() in sql_functions:
            continue

        # Skip table names
        if identifier_lower in valid_tables:
            continue

        # Skip aliases
        if identifier_lower in aliases:
            continue

        # Skip columns already checked as qualified
        if identifier_lower in qualified_column_names:
            continue

        # Check whether it is a known column
        if identifier_lower in available_columns:
            continue

        # Ignore numbers
        if identifier.isdigit():
            continue

        # Ignore common SQL literals
        if identifier.upper() in {
            "TRUE",
            "FALSE"
        }:
            continue

        return (
            False,
            f"Unknown column or identifier: {identifier}"
        )


    return True, "SQL passed schema validation."


if __name__ == "__main__":

    test_sql = """
    SELECT customer_name
    FROM customers;
    """

    is_valid, message = validate_sql(test_sql)

    print("Valid:", is_valid)
    print("Message:", message)