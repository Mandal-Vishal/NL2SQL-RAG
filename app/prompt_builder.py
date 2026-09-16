from query_vector_store import search_schema


def build_sql_prompt(question, retrieved_documents):

    schema_context = ""

    for result in retrieved_documents:

        schema_context += result["document"]
        schema_context += "\n\n"

    prompt = f"""
You are an expert MySQL Text-to-SQL system.

Your task is to convert the user's natural-language question
into a valid MySQL SQL query.

Database schema:

{schema_context}

User question:

{question}

Rules:

1. Use only tables and columns present in the provided schema.
2. Do not invent tables or columns.
3. Use the provided relationships when constructing JOINs.
4. Generate valid MySQL syntax.
5. Return only the SQL query.
6. Do not provide explanations or markdown.

SQL:
"""

    return prompt


if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    retrieved_documents = search_schema(
        question,
        3
    )

    prompt = build_sql_prompt(
        question,
        retrieved_documents
    )

    print(prompt)