from query_vector_store import search_schema
from prompt_builder import build_sql_prompt
from llm import generate_sql
from sql_validator import validate_sql
from database import execute_sql


MAX_CORRECTION_ATTEMPTS = 3
MAX_DATABASE_RETRIES = 2


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

    # =======================================
    # Pipeline information
    # =======================================

    pipeline = {
        "question": question,
        "retrieved_documents": [],
        "validation_attempts": [],
        "correction_attempts": 0,
        "execution_attempts": 0,
        "sql": None,
        "columns": [],
        "results": [],
        "success": False,
        "error": None
    }


    # =======================================
    # Step 1: Retrieve schema
    # =======================================

    try:

        retrieved_documents = search_schema(
            question,
            3
        )

        pipeline["retrieved_documents"] = (
            retrieved_documents
        )

    except Exception as error:

        pipeline["error"] = (
            f"Schema retrieval failed: {error}"
        )

        return pipeline


    # =======================================
    # Step 2: Build initial prompt
    # =======================================

    try:

        prompt = build_sql_prompt(
            question,
            retrieved_documents
        )

    except Exception as error:

        pipeline["error"] = (
            f"Prompt construction failed: {error}"
        )

        return pipeline


    # =======================================
    # Step 3: Generate initial SQL
    # =======================================

    try:

        sql = generate_sql(prompt)

    except Exception as error:

        pipeline["error"] = (
            f"LLM generation failed: {error}"
        )

        return pipeline


    # =======================================
    # Step 4: Validation + self-correction
    # =======================================

    is_valid = False

    for attempt in range(MAX_CORRECTION_ATTEMPTS):

        is_valid, message = validate_sql(sql)

        pipeline["validation_attempts"].append({
            "attempt": attempt + 1,
            "sql": sql,
            "valid": is_valid,
            "message": message
        })


        # -----------------------------------
        # SQL is valid
        # -----------------------------------

        if is_valid:

            break


        # -----------------------------------
        # Maximum attempts reached
        # -----------------------------------

        if attempt == MAX_CORRECTION_ATTEMPTS - 1:

            pipeline["error"] = (
                "Unable to generate a valid SQL query "
                "after multiple correction attempts."
            )

            return pipeline


        # -----------------------------------
        # Ask Gemini to correct SQL
        # -----------------------------------

        correction_prompt = build_correction_prompt(
            question,
            retrieved_documents,
            sql,
            message
        )


        try:

            sql = generate_sql(
                correction_prompt
            )

            pipeline["correction_attempts"] += 1

        except Exception as error:

            pipeline["error"] = (
                f"SQL correction failed: {error}"
            )

            return pipeline


    # =======================================
    # Final validation
    # =======================================

    if not is_valid:

        pipeline["error"] = (
            "Generated SQL failed validation."
        )

        return pipeline


    pipeline["sql"] = sql


    # =======================================
    # Step 5: Execute SQL
    # =======================================

    for attempt in range(MAX_DATABASE_RETRIES):

        pipeline["execution_attempts"] += 1

        try:

            columns, results = execute_sql(
                sql
            )

            pipeline["columns"] = list(
                columns
            )

            pipeline["results"] = [
                list(row)
                for row in results
            ]

            pipeline["success"] = True

            return pipeline


        except Exception as error:

            # -----------------------------------
            # Last database attempt
            # -----------------------------------

            if attempt == MAX_DATABASE_RETRIES - 1:

                pipeline["error"] = (
                    f"Database execution failed: {error}"
                )

                return pipeline


            # -----------------------------------
            # Ask Gemini to correct SQL
            # -----------------------------------

            correction_prompt = build_correction_prompt(
                question,
                retrieved_documents,
                sql,
                str(error)
            )


            try:

                corrected_sql = generate_sql(
                    correction_prompt
                )

            except Exception as llm_error:

                pipeline["error"] = (
                    f"Database failed and SQL correction "
                    f"also failed: {llm_error}"
                )

                return pipeline


            # -----------------------------------
            # Validate corrected SQL
            # -----------------------------------

            corrected_valid, corrected_message = (
                validate_sql(corrected_sql)
            )


            pipeline["validation_attempts"].append({
                "attempt": len(
                    pipeline["validation_attempts"]
                ) + 1,
                "sql": corrected_sql,
                "valid": corrected_valid,
                "message": corrected_message
            })


            if not corrected_valid:

                pipeline["error"] = (
                    "Database error correction produced "
                    "invalid SQL."
                )

                return pipeline


            sql = corrected_sql

            pipeline["sql"] = sql


    return pipeline


# ==========================================
# Direct testing
# ==========================================

if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    result = generate_query(
        question
    )

    print("\n================================")
    print("SUCCESS")
    print("================================")

    print(
        result["success"]
    )

    print("\n================================")
    print("SQL")
    print("================================")

    print(
        result["sql"]
    )

    print("\n================================")
    print("RESULTS")
    print("================================")

    for row in result["results"]:

        print(row)