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

    documents = results["documents"][0]
    distances = results["distances"][0]

    retrieved_docs = []

    for document,distance in zip(documents,distances):
        retrieved_docs.append({
            "document":document,
            "distance" : distance
        })

    return retrieved_docs

# Testing
if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    results = search_schema(question, 3)

    for result in results:

        print("Distance:", result["distance"])

        print(result["document"])

        print("=" * 60)

