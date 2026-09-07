import chromadb;
from embedding_model import create_embedding ;

# Connect to existing chromaDB
client = chromadb.PersistentClient(path = './chroma_db')

# Get existing collection
collection = client.get_collection(name = 'schema_documents')

def search_schema(question , no_of_results):

    question_embedding = create_embedding(question)

    results = collection.query(
        query_embeddings = [question_embedding.tolist()],
        n_results = no_of_results
    )

    return results

# Testing
if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    results = search_schema(question , 3)

    print("\nRelevant Schema Documents:\n")

    for document in results["documents"][0]:

        print(document)

        print("=" * 60)

