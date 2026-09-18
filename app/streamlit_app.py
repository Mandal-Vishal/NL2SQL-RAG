import streamlit as st

from nl_2_sql import generate_query


# ---------------------------------------
# Page configuration
# ---------------------------------------

st.set_page_config(
    page_title="NL2SQL RAG System",
    page_icon="🔎",
    layout="wide"
)


# ---------------------------------------
# Title
# ---------------------------------------

st.title("NL2SQL RAG System")

st.write(
    "Convert natural-language questions into SQL queries "
    "using Retrieval-Augmented Generation."
)


# ---------------------------------------
# User input
# ---------------------------------------

question = st.text_input(
    "Ask a question about the database:"
)


# ---------------------------------------
# Generate SQL
# ---------------------------------------

if st.button("Generate SQL"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            with st.spinner(
                "Generating SQL and fetching results..."
            ):

                result = generate_query(
                    question.strip()
                )


            # -----------------------------------
            # Check result
            # -----------------------------------

            if result is None:

                st.error(
                    "Unable to generate a valid SQL query."
                )

            else:

                sql, columns, results = result


                # -------------------------------
                # Generated SQL
                # -------------------------------

                st.subheader(
                    "Generated SQL"
                )

                st.code(
                    sql,
                    language="sql"
                )


                # -------------------------------
                # Query results
                # -------------------------------

                st.subheader(
                    "Query Results"
                )


                if results:

                    # Combine column names with row values
                    result_data = []

                    for row in results:

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

                else:

                    st.info(
                        "The query executed successfully, "
                        "but returned no results."
                    )

        except Exception as error:

            st.error(
                "An error occurred while processing your question."
            )

            st.exception(error)