import streamlit as st

from nl2sql import generate_query

# Page configuration
st.set_page_config(
    page_title="NL2SQL RAG System",
    page_icon="🔎",
    layout="wide"
)

# Title
st.title("NL2SQL RAG System")

st.write(
    "Convert natural-language questions into SQL queries "
    "using Retrieval-Augmented Generation."
)

# User input
question = st.text_input(
    "Ask a question about the database:"
)

# Generate SQL

if st.button("Generate SQL"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Generating SQL..."
        ):

            result = generate_query(
                question
            )

        # Check result
        if result is None:

            st.error(
                "Unable to generate a valid SQL query."
            )

        else:

            sql, columns, results = result

            # Generated SQL
            st.subheader(
                "Generated SQL"
            )

            st.code(
                sql,
                language="sql"
            )

            # Database results
            st.subheader(
                "Query Results"
            )

            if results:

                result_data = [
                    list(row)
                    for row in results
                ]

                st.dataframe(
                    result_data,
                    use_container_width=True
                )

            else:

                st.info(
                    "The query executed successfully, "
                    "but returned no results."
                )