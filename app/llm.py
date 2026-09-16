import os 
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
)

MODEL_NAME = "gemini-3.6-flash"

def generate_sql(prompt):
    interaction = client.interactions.create(
        model = MODEL_NAME,
        input = prompt
    )

    sql = interaction.output_text

    return sql

if __name__ == "__main__" :
    test_prompt = """ Generate a MySQL query that returns all customers from the Customers table who live in Mumbai. Return only the SQL query. """

    sql = generate_sql(test_prompt)

    print("Generated SQL : \n")
    print(sql)