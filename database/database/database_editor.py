import psycopg2
from psycopg2 import sql
from typing import List, Tuple, Any, Optional

class DatabaseEditor:
    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: str = "5432"):
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Function to connect to the database.
        """
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor()
            print("Connected to the database successfully.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while connecting to PostgreSQL: {error}")

    def close_connection(self):
        """
        Function to close the connection to the database.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_table(self, table_name: str, columns: List[Tuple[str, str]], 
                     primary_key: Optional[str] = None, 
                     foreign_keys: Optional[List[Tuple[str, str, str]]] = None):
        """
        Function to create a table in the database.
        """
        try:
            column_defs = [sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(type_)) for name, type_ in columns]
            
            if primary_key:
                column_defs.append(sql.SQL("PRIMARY KEY ({})").format(sql.Identifier(primary_key)))
            
            if foreign_keys:
                for fk_column, ref_table, ref_column in foreign_keys:
                    fk_def = sql.SQL("FOREIGN KEY ({}) REFERENCES {} ({})").format(
                        sql.Identifier(fk_column),
                        sql.Identifier(ref_table),
                        sql.Identifier(ref_column)
                    )
                    column_defs.append(fk_def)
            
            query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(column_defs)
            )
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Table '{table_name}' created successfully.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while creating table: {error}")

    def insert_row(self, table_name: str, data: dict):
        """
        Function to insert a single row of data to a given table in the database.
        """
        try:
            columns = data.keys()
            values = [data[column] for column in columns]
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Data inserted successfully.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while inserting data: {error}")

    def insert_multiple_rows(self, table_name: str, data: List[dict]):
        """
        Function to insert multiple rows to a given table in the database.
        """
        try:
            if not data:
                print("No data to insert.")
                return

            columns = data[0].keys()
            values = [tuple(row[column] for column in columns) for row in data]
            placeholders = sql.SQL(',').join([sql.SQL('({})').format(sql.SQL(',').join([sql.Placeholder()] * len(columns)))] * len(data))
            
            query = sql.SQL("INSERT INTO {} ({}) VALUES {}").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                placeholders
            )
            
            flattened_values = [item for sublist in values for item in sublist]
            self.cursor.execute(query, flattened_values)
            self.conn.commit()
            print(f"{len(data)} rows inserted successfully.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while inserting multiple rows: {error}")
            self.conn.rollback()

    def select_data(self, table_name: str, columns: List[str] = None, condition: str = None):
        """
        Function to retrieve data from a given table in the database.
        """
        try:
            if columns:
                column_names = sql.SQL(', ').join(map(sql.Identifier, columns))
            else:
                column_names = sql.SQL('*')

            query = sql.SQL("SELECT {} FROM {}").format(column_names, sql.Identifier(table_name))

            if condition:
                query += sql.SQL(" WHERE {}").format(sql.SQL(condition))

            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            if not rows:
                print("No data found.")
                return

            # Print column names
            if columns:
                print(" | ".join(columns))
            else:
                print(" | ".join([desc[0] for desc in self.cursor.description]))

            # Print rows
            for row in rows:
                print(" | ".join(str(value) for value in row))

        except (Exception, psycopg2.Error) as error:
            print(f"Error while selecting data: {error}")

    def update_table(self, table_name: str, set_values: dict, condition: str):
        """
        Function to update row in a given table in the database.
        """
        try:
            set_items = [sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder()) for k in set_values.keys()]
            query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(set_items),
                sql.SQL(condition)
            )
            self.cursor.execute(query, list(set_values.values()))
            self.conn.commit()
            print(f"{self.cursor.rowcount} row(s) updated successfully.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while updating table: {error}")

    def delete_row(self, table_name: str, condition: str, cascade: bool = False):
        """
        Function to delete a single row from a given table in the database.
        """
        try:
            if cascade:
                # Find all tables with foreign key references to this table
                self.cursor.execute("""
                    SELECT
                        tc.table_schema, 
                        tc.constraint_name, 
                        tc.table_name, 
                        kcu.column_name, 
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                          AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                          AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND ccu.table_name = %s
                """, (table_name,))
                
                referring_tables = self.cursor.fetchall()

                # For each referring table, delete the referring rows
                for _, _, ref_table, ref_column, _, _, _ in referring_tables:
                    delete_query = sql.SQL("DELETE FROM {} WHERE {} IN (SELECT id FROM {} WHERE {})").format(
                        sql.Identifier(ref_table),
                        sql.Identifier(ref_column),
                        sql.Identifier(table_name),
                        sql.SQL(condition)
                    )
                    self.cursor.execute(delete_query)

            # Now delete from the main table
            query = sql.SQL("DELETE FROM {} WHERE {}").format(sql.Identifier(table_name), sql.SQL(condition))
            self.cursor.execute(query)
            self.conn.commit()
            print(f"{self.cursor.rowcount} row(s) deleted successfully.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while deleting row: {error}")
            self.conn.rollback()

    def delete_table(self, table_name: str):
        """
        Function to delete the given table from the database.
        """
        try:
            query = sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name))
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Table '{table_name}' deleted successfully.")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while deleting table: {error}")

