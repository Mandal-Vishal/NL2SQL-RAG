import streamlit as st
from sentence_transformers import SentenceTransformer


@st.cache_resource
def load_embedding_model():

    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


def create_embedding(text):

    model = load_embedding_model()

    embedding = model.encode(text)

    return embedding


if __name__ == "__main__":

    text = "Which customers rented Honda cars?"

    embedding = create_embedding(text)

    print("Embedding type:", type(embedding))
    print("Embedding dimensions:", len(embedding))
    print("First 10 values:", embedding[:10])