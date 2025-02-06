import sqlite3
import pandas as pd
from tabulate import tabulate

class SQLiteViewer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect('example.db')
            self.cursor = self.conn.cursor()
            print(f"Successfully connected to {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def get_tables(self):
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()
            return [table[0] for table in tables]
        except sqlite3.Error as e:
            print(f"Error getting tables: {e}")
            return []

    def get_table_info(self, table_name):
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns = self.cursor.fetchall()
            return [(col[1], col[2]) for col in columns]
        except sqlite3.Error as e:
            print(f"Error getting table info: {e}")
            return []

    def view_table_data(self, table_name, limit=10):
        try:
            # Get data using pandas
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", self.conn)
            print(f"\nTable: {table_name}")
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
            print(f"\nTotal rows in table: {self.get_row_count(table_name)}")
        except sqlite3.Error as e:
            print(f"Error viewing table data: {e}")

    def get_row_count(self, table_name):
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting row count: {e}")
            return 0

    def run_query(self, query):
        try:
            df = pd.read_sql_query(query, self.conn)
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

def main():
    db_path = input("Enter the path to your SQLite database: ")
    viewer = SQLiteViewer(db_path)
    viewer.connect()

    while True:
        print("\n=== SQLite Database Viewer ===")
        print("1. List tables")
        print("2. View table structure")
        print("3. View table data")
        print("4. Run custom query")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ")

        if choice == '1':
            tables = viewer.get_tables()
            print("\nTables in database:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")

        elif choice == '2':
            tables = viewer.get_tables()
            print("\nAvailable tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            table_idx = int(input("Enter table number: ")) - 1
            if 0 <= table_idx < len(tables):
                table_info = viewer.get_table_info(tables[table_idx])
                print("\nColumn Name | Data Type")
                print("-" * 30)
                for col_name, col_type in table_info:
                    print(f"{col_name:<11} | {col_type}")

        elif choice == '3':
            tables = viewer.get_tables()
            print("\nAvailable tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            table_idx = int(input("Enter table number: ")) - 1
            if 0 <= table_idx < len(tables):
                limit = input("Enter number of rows to view (default 10): ") or 10
                viewer.view_table_data(tables[table_idx], limit)

        elif choice == '4':
            query = input("Enter your SQL query: ")
            viewer.run_query(query)

        elif choice == '5':
            viewer.close()
            break

if __name__ == "__main__":
    main()