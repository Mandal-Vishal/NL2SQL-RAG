from query_vector_store import search_schema
from prompt_builder import build_sql_prompt
from llm import generate_sql


def generate_query(question):

    # Step 1: Retrieve relevant schema
    retrieved_documents = search_schema(
        question,
        3
    )

    # Step 2: Build the prompt
    prompt = build_sql_prompt(
        question,
        retrieved_documents
    )

    # Step 3: Generate SQL using Gemini
    sql = generate_sql(prompt)

    return sql


if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    sql = generate_query(question)

    print("\nGenerated SQL:\n")
    print(sql)