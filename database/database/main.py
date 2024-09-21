from database_editor import DatabaseEditor
import pandas as pd

# provide the table to connect to and its primary key
table_name = ''
primary_key = ''

table = DatabaseEditor(
    user='',
    password='',
    host='localhost',
    port='5432',
    dbname='',
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
