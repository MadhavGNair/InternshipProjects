from database_editor import DatabaseEditor
import pandas as pd

'''
TABLES LEFT TO POPULATE:
    - doc
    - paragraph
    - sentence
    - semantic_data
    - query
    - area
'''

# provide the table to connect to and its primary key
table_name = 'mn_doc'
primary_key = 'doc_hash'

table = DatabaseEditor(
    user='nair6468',
    password='M@$tu4ig972',
    host='localhost',
    port='5432',
    dbname='devdb',
    table=table_name,
    primary_key=primary_key
)

table.connect()

# load the data from CSV file
path = './csv_data/sgx.csv'
df = pd.read_csv(path)

# extract the company_id representing the company_name


columns = ('doc_hash', 'company_id', 'doc_name', 'pub_year', 'type', 'local_path')
data = [[int(x[2].item()), int(x[1].item()), x[3].item(), int(x[4].item())] for x in df.to_numpy()]

for item in data[:10]:
    print(item)



# insert using the table column names
# table.insert_many(columns, data)

table.commit()
table.close()
