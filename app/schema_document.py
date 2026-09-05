from schema_inspector import get_schema;

def schema_doc():
    schema = get_schema()

    docs = []

    for table_name , table_data in schema.items():
            doc = f'Table:{table_name}\n\n'
            doc += f'Columns:\n'

            for column in table_data['columns']:
                  doc+=(
                        f'- {column['name']} '
                        f' {column['type']}'
                  )

                  if column['key'] == 'PRI':
                        doc+=' [PRIMARY KEY]'

                  elif column['key'] == 'UNI':
                        doc+=' [UNIQUE]'

                  doc+='\n'


            if table_data['foreign_keys']:

                for fk in table_data['foreign_keys']:

                    doc += (
                          f'- {fk['column']} references'
                          f' - {fk['references']}\n'
                    )

            docs.append(doc)
    return docs

if __name__ == '__main__':
      docs = schema_doc()

      for doc in docs:
            print(doc)