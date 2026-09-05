from schema_document import schema_doc;
from embedding_model import create_embedding;

import numpy as np;

def cosine_similarity(vector1,vector2):
    similarity = np.dot(vector1,vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))

    return similarity

def find_relevant_documents(question , documents):
    question_embedding = create_embedding(question)

    results = []

    for document in documents:
        document_embedding = create_embedding(document)

        score  = cosine_similarity(question_embedding,document_embedding)

        results.append((score,document))

    results.sort(reverse=True)

    return results

if __name__ == "__main__":

    question = "Which customers rented Honda cars?"

    documents = schema_doc()

    results = find_relevant_documents(
        question,
        documents
    )

    for score, document in results:

        print(f"\nSimilarity: {score:.4f}")

        print(document)

        print("=" * 60)