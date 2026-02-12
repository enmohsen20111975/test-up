"""
Migration script to enhance the database schema for equations and workflows.
Adds support for:
- Input patterns and validation
- Enhanced categorization (subcategories, tags, difficulty)
- Better units support
- Additional metadata (description, references, examples)
"""
import sqlite3
import json
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def migrate_database(db_path='workflows.db'):
    """Migrate the database to the enhanced schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(calculation_variables)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Add new columns to calculation_variables table
    new_columns = {
        'data_type': 'VARCHAR',
        'default_value': 'VARCHAR',
        'min_value': 'FLOAT',
        'max_value': 'FLOAT',
        'validation_pattern': 'VARCHAR',
        'unit_system': 'VARCHAR',
        'conversion_factor': 'FLOAT',
        'is_required': 'BOOLEAN',
        'display_order': 'INTEGER'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE calculation_variables ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column '{col_name}' to calculation_variables")
            except sqlite3.OperationalError as e:
                print(f"  [ERROR] Error adding column '{col_name}': {e}")
        else:
            print(f"  - Column '{col_name}' already exists")
    
    # Add new columns to calculations table
    cursor.execute("PRAGMA table_info(calculations)")
    existing_calc_columns = [row[1] for row in cursor.fetchall()]
    
    new_calc_columns = {
        'description': 'TEXT',
        'difficulty': 'VARCHAR',
        'tags': 'TEXT',
        'reference': 'VARCHAR',
        'example_input': 'TEXT',
        'example_output': 'TEXT',
        'notes': 'TEXT',
        'is_active': 'BOOLEAN',
        'created_at': 'DATETIME',
        'updated_at': 'DATETIME'
    }
    
    for col_name, col_type in new_calc_columns.items():
        if col_name not in existing_calc_columns:
            try:
                cursor.execute(f"ALTER TABLE calculations ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column '{col_name}' to calculations")
            except sqlite3.OperationalError as e:
                print(f"  [ERROR] Error adding column '{col_name}': {e}")
        else:
            print(f"  - Column '{col_name}' already exists")
    
    # Add new columns to calculation_categories table
    cursor.execute("PRAGMA table_info(calculation_categories)")
    existing_cat_columns = [row[1] for row in cursor.fetchall()]
    
    new_cat_columns = {
        'description': 'TEXT',
        'icon': 'VARCHAR',
        'color': 'VARCHAR',
        'display_order': 'INTEGER',
        'is_active': 'BOOLEAN'
    }
    
    for col_name, col_type in new_cat_columns.items():
        if col_name not in existing_cat_columns:
            try:
                cursor.execute(f"ALTER TABLE calculation_categories ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column '{col_name}' to calculation_categories")
            except sqlite3.OperationalError as e:
                print(f"  [ERROR] Error adding column '{col_name}': {e}")
        else:
            print(f"  - Column '{col_name}' already exists")
    
    # Add new columns to workflow_inputs table
    cursor.execute("PRAGMA table_info(workflow_inputs)")
    existing_wf_in_columns = [row[1] for row in cursor.fetchall()]
    
    new_wf_in_columns = {
        'data_type': 'VARCHAR',
        'default_value': 'VARCHAR',
        'validation_pattern': 'VARCHAR',
        'unit': 'VARCHAR',
        'display_order': 'INTEGER'
    }
    
    for col_name, col_type in new_wf_in_columns.items():
        if col_name not in existing_wf_in_columns:
            try:
                cursor.execute(f"ALTER TABLE workflow_inputs ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column '{col_name}' to workflow_inputs")
            except sqlite3.OperationalError as e:
                print(f"  [ERROR] Error adding column '{col_name}': {e}")
        else:
            print(f"  - Column '{col_name}' already exists")
    
    # Add new columns to workflows table
    cursor.execute("PRAGMA table_info(workflows)")
    existing_wf_columns = [row[1] for row in cursor.fetchall()]
    
    new_wf_columns = {
        'difficulty': 'VARCHAR',
        'estimated_time': 'VARCHAR',
        'tags': 'TEXT',
        'is_active': 'BOOLEAN',
        'created_at': 'DATETIME',
        'updated_at': 'DATETIME'
    }
    
    for col_name, col_type in new_wf_columns.items():
        if col_name not in existing_wf_columns:
            try:
                cursor.execute(f"ALTER TABLE workflows ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column '{col_name}' to workflows")
            except sqlite3.OperationalError as e:
                print(f"  [ERROR] Error adding column '{col_name}': {e}")
        else:
            print(f"  - Column '{col_name}' already exists")
    
    # Add new columns to workflow_categories table
    cursor.execute("PRAGMA table_info(workflow_categories)")
    existing_wf_cat_columns = [row[1] for row in cursor.fetchall()]
    
    new_wf_cat_columns = {
        'description': 'TEXT',
        'icon': 'VARCHAR',
        'color': 'VARCHAR',
        'display_order': 'INTEGER',
        'is_active': 'BOOLEAN'
    }
    
    for col_name, col_type in new_wf_cat_columns.items():
        if col_name not in existing_wf_cat_columns:
            try:
                cursor.execute(f"ALTER TABLE workflow_categories ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column '{col_name}' to workflow_categories")
            except sqlite3.OperationalError as e:
                print(f"  [ERROR] Error adding column '{col_name}': {e}")
        else:
            print(f"  - Column '{col_name}' already exists")
    
    conn.commit()
    conn.close()
    print("\n[OK] Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
