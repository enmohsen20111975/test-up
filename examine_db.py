import sqlite3
import json
import os

# Examine workflows.db
print("=== WORKFLOWS.DB ===")
conn = sqlite3.connect('workflows.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")

# Examine each table
for table in tables:
    table_name = table[0]
    print(f"\n--- Table: {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("Columns:", columns)
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Rows: {count}")
    
    # Show some sample data
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print("Sample data:", rows)

conn.close()

# Examine engisuite.db
print("\n\n=== ENGISUITE.DB ===")
conn = sqlite3.connect('engisuite.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")

for table in tables:
    table_name = table[0]
    print(f"\n--- Table: {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("Columns:", columns)
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Rows: {count}")

conn.close()
 