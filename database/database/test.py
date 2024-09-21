from database_editor import DatabaseEditor
import random

# def extract_companies_to_list(filename):
#     companies = []
#     with open(filename, 'r') as file:
#         for line in file:
#             company = line.strip()
#             if company:
#                 companies.append(company)
#     return companies

# table_name = 'mn_company'
# primary_key = 'id'

# table = DatabaseEditor(
#     user='nair6468',
#     password='M@$tu4ig972',
#     host='localhost',
#     port='5432',
#     dbname='devdb',
#     table=table_name,
#     primary_key=primary_key
# )

# table.connect()

# columns = ('company_name', 'headquarters')
# locations =  [
#     "Brazil",
#     "Canada",
#     "Japan",
#     "Australia",
#     "Germany",
#     "South Africa",
#     "India",
#     "Mexico",
#     "Sweden",
#     "Egypt",
#     "Thailand",
#     "Argentina",
#     "Morocco",
#     "New Zealand",
#     "Italy"
# ]
# values = [[companies, random.choice(locations)] for companies in extract_companies_to_list('unique_companies.txt')]

# # print(values[0])

# table.insert_many(columns, values)

# table.commit()
# table.close()

import psycopg2
import csv

# Database connection parameters
db_params = {
    "host": "localhost",
    "database": "devdb",
    "user": "nair6468",
    "password": "M@$tu4ig972"
}

def get_company_id(cursor, company_name):
    # Normalize company name to uppercase for comparison
    normalized_name = company_name.upper()
    
    # Query to get company_id based on normalized company name
    query = """
    SELECT id 
    FROM mn_company 
    WHERE UPPER(company_name) = %s
    """
    
    cursor.execute(query, (normalized_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        return None

def main():
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Open and read the CSV file
    with open('./csv_data/sgx.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        # Prepare data for batch insert
        insert_data = []
        
        for row in csv_reader:
            company_name = row['company_id'].strip()
            company_id = get_company_id(cursor, company_name)
            
            if company_id is not None:
                insert_data.append((
                    row['doc_hash'],
                    company_id,
                    row['doc_name'],
                    row['pub_year'],
                    row['type'],
                    row['local_path']
                ))
                print(row)
                break
            else:
                print(f"Warning: No matching company ID found for '{company_name}'")

    # Batch insert into mn_doc table
    insert_query = """
    INSERT INTO mn_doc (doc_hash, company_id, doc_name, pub_year, type, local_path)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, insert_data)

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()


final_data = main()

