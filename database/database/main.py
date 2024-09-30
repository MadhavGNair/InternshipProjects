from database_editor import DatabaseEditor
import pandas as pd
import random
import numpy as np

# # EXAMPLE 1: TO CREATE A TABLE (WITH AND WITHOUT FOREIGN KEYS)

# db = DatabaseEditor("db name", "username", "password")
# db.connect()

# # WITHOUT FOREIGN KEYS: create a table called 'mn_departments' with columns 'id' and 'name'
# db.create_table(
#     "mn_test",
#     [("id", "SERIAL"), ("name", "VARCHAR(100)")],
#     primary_key="id"
# )

# # WITH FOREIGN KEYS: create a table called 'mn_employees' with columns 'id', 'name', and 'department_id' but
# # 'department_id' is a foreign key referring to table 'mn_departments'. Format of foreign key definition is
# # [('key in current table', 'table being referred to', 'key in the referred table')] 
# db.create_table(
#     "mn_employees",
#     [("id", "SERIAL"), ("name", "VARCHAR(100)"), ("department_id", "INTEGER")],
#     primary_key="id",
#     foreign_keys=[("department_id", "mn_departments", "id")]
# )

# db.close_connection()


# ===============================================================================================================


# # EXAMPLE 2: TO INSERT DATA TO TABLE

# connect to the database
# db = DatabaseEditor("db name", "username", "password")
# db.connect()

# # insert a single row into the 'mn_departments' table
# db.insert_row("mn_departments", {"name": "Human Resources"})

# # insert multiple rows into the 'mn_departments' table
# # NOTE: this is useful when you want to insert large amounts of data from a CSV file as long as you format the data
# # as a dict.
# mn_departments_data = [
#     {"name": "Engineering"},
#     {"name": "Marketing"},
#     {"name": "Finance"}
# ]
# db.insert_multiple_rows("mn_departments", mn_departments_data)

# # Select and print all mn_departments to verify the insertions
# print("mn_Departments:")
# db.select_data("mn_departments")

# # Insert a single row into the 'mn_employees' table
# # Assuming the 'Human Resources' department has id 1
# db.insert_row("mn_employees", {"name": "John Doe", "department_id": 1})

# # Insert multiple rows into the 'mn_employees' table
# # Assuming Engineering, Marketing, and Finance have ids 2, 3, and 4 respectively
# mn_employees_data = [
#     {"name": "Jane Smith", "department_id": 2},
#     {"name": "Mike Johnson", "department_id": 3},
#     {"name": "Emily Brown", "department_id": 4},
#     {"name": "Chris Lee", "department_id": 2}
# ]
# db.insert_multiple_rows("mn_employees", mn_employees_data)

# # Select and print all mn_employees to verify the insertions
# print("\nmn_Employees:")
# db.select_data("mn_employees")

# # Close the database connection
# db.close_connection()


# ===============================================================================================================


# # EXAMPLE 3: UPDATING THE DATABASE
# # connect to the database
# db = DatabaseEditor("db name", "username", "password")
# db.connect()

# # update the name of the "Marketing" department to "Digital Marketing"
# # NOTE: the quotes in the 'condition' are very important
# db.update_table(
#     table_name="mn_departments",
#     set_values={"name": "Digital Marketing"},
#     condition="name = 'Marketing'"
# )

# # update the "Jane Smith" name to "Jane Doe"
# db.update_table(
#     table_name="mn_employees",
#     set_values={"name": "Jane Doe"},
#     condition="name = 'Jane Smith'"
# )

# # print the state of the table after updates
# print("\nAfter update:")
# db.select_data("mn_employees")

# # close the database connection
# db.close_connection()


# ===============================================================================================================


# # EXAMPLE 4: DELETING FROM THE DATABASE (ROW AND TABLE)
# # connect to the database
# db = DatabaseEditor("db name", "username", "password")
# db.connect()

# # delete a single row to remove a specific department
# print("\nDeleting the Marketing department:")
# db.delete_row(
#     table_name="mn_departments",
#     condition="name = 'Digital Marketing'"
# )

# # Print the state of the table after deleting a row
# print("\nAfter deleting Digital Marketing:")
# db.select_data("mn_departments")

# # NOTE: THE ABOVE CODE WILL GIVE YOU AN ERROR SINCE 'MN_EMPLOYEES' ACTUALLY REFERS TO 'DIGITAL MARKETING' SO IT STOPS
# # YOU FROM DELETING. THIS IS A GOOD ERROR SO I DO NOT OVERRIDE IT. IF YOU WANT TO OVERRIDE THE ERROR, CHANGE THE FUNCTION 
# # CALL LIKE THIS:
# # db.delete_row(
# #     table_name="mn_departments",
# #     condition="name = 'Digital Marketing'",
# #     cascade=True
# # )
# # THIS MUST ONLY BE DONE IF YOU ARE ABSOLUTELY SURE BECAUSE THIS DELETES THE ROW AS WELL AS ALL ROWS RELATED TO IT (AND MORE
# # ROWS RELATED TO ANY DELETED ROW)

# # delete_row with a condition that matches multiple rows
# print("\nDeleting all departments that start with 'F':")
# db.delete_row(
#     table_name="mn_departments",
#     condition="name LIKE 'F%'"
# )

# # print the state of the table after deleting multiple rows
# print("\nAfter deleting departments starting with 'F':")
# db.select_data("mn_departments")

# # using delete_table to remove the entire table
# print("\nDeleting the entire mn_departments table:")
# db.delete_table("mn_departments")

# # try to select data from the deleted table to verify it's gone
# print("\nAttempting to select data from deleted table:")
# db.select_data("mn_departments")

# # Close the database connection
# db.close_connection()