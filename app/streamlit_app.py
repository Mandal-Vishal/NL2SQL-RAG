import streamlit as st

from nl_2_sql import generate_query


# ==========================================
# Page configuration
# ==========================================

st.set_page_config(
    page_title="NL2SQL RAG System",
    page_icon="🔎",
    layout="wide"
)


# ==========================================
# Header
# ==========================================

st.title(
    "NL2SQL RAG System"
)

st.write(
    "Convert natural-language questions into "
    "SQL queries using Retrieval-Augmented Generation."
)


# ==========================================
# Question input
# ==========================================

question = st.text_input(
    "Ask a question about the database:",
    placeholder="Example: Which customers rented Honda cars?"
)


# ==========================================
# Generate button
# ==========================================

if st.button(
    "Generate SQL",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            with st.spinner(
                "Running NL2SQL pipeline..."
            ):

                result = generate_query(
                    question.strip()
                )


            # ==================================
            # Pipeline failed
            # ==================================

            if not result["success"]:

                st.error(
                    "Unable to process the question."
                )

                if result["error"]:

                    st.warning(
                        result["error"]
                    )


            else:

                # ==================================
                # Success message
                # ==================================

                st.success(
                    "Query generated and executed successfully."
                )


                # ==================================
                # RAG Retrieval
                # ==================================

                st.subheader(
                    "1. Retrieved Schema"
                )

                st.write(
                    "The following schema information was "
                    "retrieved from ChromaDB for this question."
                )


                retrieved_documents = (
                    result["retrieved_documents"]
                )


                for index, document in enumerate(
                    retrieved_documents
                ):

                    with st.expander(
                        f"Retrieved Document {index + 1}"
                    ):

                        st.code(
                            document["document"],
                            language="text"
                        )

                        st.caption(
                            f"Retrieval distance: "
                            f"{document['distance']:.4f}"
                        )


                # ==================================
                # Generated SQL
                # ==================================

                st.subheader(
                    "2. Generated SQL"
                )

                st.code(
                    result["sql"],
                    language="sql"
                )


                # ==================================
                # Validation
                # ==================================

                st.subheader(
                    "3. SQL Validation"
                )


                validation_attempts = (
                    result["validation_attempts"]
                )


                for validation in validation_attempts:

                    if validation["valid"]:

                        st.success(
                            f"Attempt "
                            f"{validation['attempt']}: "
                            f"{validation['message']}"
                        )

                    else:

                        st.error(
                            f"Attempt "
                            f"{validation['attempt']}: "
                            f"{validation['message']}"
                        )


                # ==================================
                # Self-correction
                # ==================================

                st.subheader(
                    "4. Self-Correction"
                )


                if result["correction_attempts"] == 0:

                    st.info(
                        "No SQL correction was required."
                    )

                else:

                    st.success(
                        f"Gemini performed "
                        f"{result['correction_attempts']} "
                        f"SQL correction attempt(s)."
                    )


                # ==================================
                # Database execution
                # ==================================

                st.subheader(
                    "5. Database Execution"
                )


                st.success(
                    f"SQL executed successfully "
                    f"in {result['execution_attempts']} "
                    f"attempt(s)."
                )


                # ==================================
                # Query results
                # ==================================

                st.subheader(
                    "6. Query Results"
                )


                columns = result["columns"]
                rows = result["results"]


                if rows:

                    result_data = []


                    for row in rows:

                        result_row = {}


                        for column, value in zip(
                            columns,
                            row
                        ):

                            result_row[column] = value


                        result_data.append(
                            result_row
                        )


                    st.dataframe(
                        result_data,
                        use_container_width=True,
                        hide_index=True
                    )


                    st.caption(
                        f"{len(rows)} row(s) returned."
                    )

                else:

                    st.info(
                        "The query executed successfully, "
                        "but returned no rows."
                    )


        except Exception as error:

            st.error(
                "An unexpected error occurred."
            )

            st.exception(error)