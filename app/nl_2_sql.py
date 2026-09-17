from query_vector_store import search_schema
from prompt_builder import build_sql_prompt
from llm import generate_sql
from sql_validator import validate_sql
from database import execute_sql


MAX_CORRECTION_ATTEMPTS = 3


def build_correction_prompt(
    question,
    retrieved_documents,
    sql,
    error_message
):

    schema_context = ""

    for result in retrieved_documents:

        schema_context += result["document"]
        schema_context += "\n\n"

    correction_prompt = f"""
You are an expert MySQL Text-to-SQL system.

The SQL query you generated is invalid.

Database schema:

{schema_context}

Original user question:

{question}

Previous SQL:

{sql}

Error:

{error_message}

Generate a corrected SQL query.

Rules:

1. Use only tables and columns present in the provided schema.
2. Use the provided relationships when constructing JOINs.
3. Use valid MySQL syntax.
4. Only generate SELECT queries.
5. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or RENAME.
6. Return only the SQL query.
"""

    return correction_prompt


def generate_query(question):

    # Step 1: Retrieve relevant schema
    retrieved_documents = search_schema(
        question,
        3
    )

    # Step 2: Build initial prompt
    prompt = build_sql_prompt(
        question,
        retrieved_documents
    )

    # Step 3: Generate initial SQL
    sql = generate_sql(prompt)
    sql = """
SELECT customer_name
FROM Customers;
"""

    # Step 4: Validation + correction loop
    for attempt in range(MAX_CORRECTION_ATTEMPTS):

        print(
            f"\nValidation attempt "
            f"{attempt + 1}/{MAX_CORRECTION_ATTEMPTS}"
        )

        is_valid, message = validate_sql(sql)

        print("Validation:", message)

        if is_valid:

            print("SQL passed validation.")

            break

        print("SQL is invalid.")

        # Maximum attempts reached
        if attempt == MAX_CORRECTION_ATTEMPTS - 1:

            print(
                "Maximum correction attempts reached."
            )

            return None

        # Ask Gemini to correct SQL
        correction_prompt = build_correction_prompt(
            question,
            retrieved_documents,
            sql,
            message
        )

        sql = generate_sql(correction_prompt)

    # Step 5: Final safety check
    if not is_valid:

        return None

    # Step 6: Execute SQL
    print("\nExecuting SQL...")

    try:

        columns, results = execute_sql(sql)

    except Exception as error:

        print("\nDatabase execution error:")
        print(error)

        # -----------------------------------
        # Database error correction
        # -----------------------------------

        correction_prompt = build_correction_prompt(
            question,
            retrieved_documents,
            sql,
            str(error)
        )

        corrected_sql = generate_sql(
            correction_prompt
        )

        # Validate corrected SQL
        is_valid, message = validate_sql(
            corrected_sql
        )

        print("\nValidation after database error:")
        print(message)

        if not is_valid:

            print(
                "Corrected SQL is still invalid."
            )

            return None

        # Try executing corrected SQL
        try:

            columns, results = execute_sql(
                corrected_sql
            )

            sql = corrected_sql

        except Exception as second_error:

            print(
                "\nSecond database execution failed:"
            )

            print(second_error)

            return None

    return sql, columns, results


if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    result = generate_query(question)

    if result is not None:

        sql, columns, results = result

        print("\n================================")
        print("FINAL SQL")
        print("================================")

        print(sql)

        print("\n================================")
        print("COLUMNS")
        print("================================")

        print(columns)

        print("\n================================")
        print("DATABASE RESULTS")
        print("================================")

        for row in results:
            print(row)