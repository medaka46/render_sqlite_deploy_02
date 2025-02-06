import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

class SQLiteViewerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite Database Viewer")
        self.root.geometry("800x600")
        
        self.conn = None
        self.current_table = None
        
        self.setup_gui()

    def setup_gui(self):
        # Database connection frame
        connection_frame = ttk.LabelFrame(self.root, text="Database Connection", padding=5)
        connection_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(connection_frame, text="Open Database", command=self.open_database).pack(side='left', padx=5)
        self.connection_label = ttk.Label(connection_frame, text="No database connected")
        self.connection_label.pack(side='left', padx=5)

        # Table selection frame
        table_frame = ttk.LabelFrame(self.root, text="Tables", padding=5)
        table_frame.pack(fill='x', padx=5, pady=5)

        self.table_combo = ttk.Combobox(table_frame, state='disabled')
        self.table_combo.pack(side='left', padx=5)
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_select)

        # Query frame
        query_frame = ttk.LabelFrame(self.root, text="Custom Query", padding=5)
        query_frame.pack(fill='x', padx=5, pady=5)

        self.query_entry = ttk.Entry(query_frame)
        self.query_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(query_frame, text="Run Query", command=self.run_query).pack(side='left', padx=5)

        # Results frame
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=5)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Treeview for displaying results
        self.tree = ttk.Treeview(results_frame)
        self.tree.pack(fill='both', expand=True, side='left')

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

    def open_database(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")])
        if file_path:
            try:
                if self.conn:
                    self.conn.close()
                self.conn = sqlite3.connect(file_path)
                self.connection_label.config(text=f"Connected: {file_path}")
                self.load_tables()
                self.table_combo.config(state='readonly')
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error opening database: {e}")

    def load_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        self.table_combo['values'] = tables
        if tables:
            self.table_combo.set(tables[0])
            self.on_table_select(None)

    def on_table_select(self, event):
        table = self.table_combo.get()
        if table:
            self.current_table = table
            self.display_table_data(table)

    def display_table_data(self, table_name):
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            self.display_dataframe(df)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error displaying table: {e}")

    def run_query(self):
        query = self.query_entry.get()
        if query:
            try:
                df = pd.read_sql_query(query, self.conn)
                self.display_dataframe(df)
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error executing query: {e}")

    def display_dataframe(self, df):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Configure columns
        self.tree['columns'] = list(df.columns)
        self.tree['show'] = 'headings'

        # Set column headings
        for column in df.columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)  # Adjust width as needed

        # Add data
        for i, row in df.iterrows():
            self.tree.insert("", 'end', values=list(row))

def main():
    root = tk.Tk()
    app = SQLiteViewerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()