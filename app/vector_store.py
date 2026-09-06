import chromadb;
from schema_document import schema_doc;
from embedding_model import create_embedding;

# Create a Persistent ChromaDB client
client = chromadb.PersistentClient(path='./chroma_db')

# Create or load a collection
collection = client.get_or_create_collection(name='schema_documents')

def store_schema_documents():
    documents = schema_doc()

    ids = []
    embeddings = []

    for index , document in enumerate(documents):

        ids.append(f'schema_{index}')

        embedding = create_embedding(document)
        embeddings.append(embedding.tolist())

    collection.add(
        ids = ids,
        documents = documents,
        embeddings = embeddings
    )

    print("Schema doc created successfully.")

if __name__ == "__main__":

    store_schema_documents()
        