from query_vector_store import search_schema
from prompt_builder import build_sql_prompt
from llm import generate_sql
from sql_validator import validate_sql
from database import execute_sql

def generate_query(question):

    # ---------------------------------------
    # Step 1: Retrieve relevant schema
    # ---------------------------------------

    retrieved_documents = search_schema(
        question,
        3
    )

    # ---------------------------------------
    # Step 2: Build initial prompt
    # ---------------------------------------

    prompt = build_sql_prompt(
        question,
        retrieved_documents
    )

    # ---------------------------------------
    # Step 3: Generate SQL
    # ---------------------------------------

    sql = generate_sql(prompt)

    # ---------------------------------------
    # Step 4: Validate generated SQL
    # ---------------------------------------

    is_valid, message = validate_sql(sql)

    print("\nValidation result:")
    print(message)

    # ---------------------------------------
    # Step 5: Self-correction
    # ---------------------------------------

    if not is_valid:

        correction_prompt = f"""
You are an expert MySQL Text-to-SQL system.

The SQL query you previously generated is invalid.

Database schema:

{''.join(
    result["document"] + "\n\n"
    for result in retrieved_documents
)}

Original user question:

{question}

Previous SQL:

{sql}

Validation error:

{message}

Correct the SQL query.

Rules:

1. Use only tables and columns from the provided schema.
2. Use the provided relationships when constructing JOINs.
3. Use valid MySQL syntax.
4. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
5. Return only the corrected SQL query.
"""

        sql = generate_sql(correction_prompt)

        # ---------------------------------------
        # Validate corrected SQL
        # ---------------------------------------

        is_valid, message = validate_sql(sql)

        print("\nAfter self-correction:")
        print(message)

    # ---------------------------------------
    # Step 6: Final safety gate
    # ---------------------------------------

    if not is_valid:

        print("\nSQL is still invalid.")
        print("Query will NOT be executed.")

        return None

    # ---------------------------------------
    # Step 7: Execute validated SQL
    # ---------------------------------------

    print("\nExecuting SQL...")

    columns, results = execute_sql(sql)

    return sql, columns, results


if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    result = generate_query(question)

    if result is not None:

        sql, columns, results = result

        print("\nFinal SQL:")
        print(sql)

        print("\nColumns:")
        print(columns)

        print("\nDatabase Results:")

        for row in results:
            print(row)