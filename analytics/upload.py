import pandas as pd
import json
from io import StringIO
import io
import re
import sqlite3

# Optional database driver imports
try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    import mysql.connector
except ImportError:
    mysql_connector = None

try:
    import pyodbc  # For SQL Server
except ImportError:
    pyodbc = None


def _validate_table_name(name: str) -> str:
    """Validate and sanitize table name to prevent SQL injection."""
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid table name: {name}")
    return name

class FileUploadService:
    @staticmethod
    def process_file(file_content: bytes, filename: str, sheet_name: str = None):
        """Process uploaded files with support for multiple sheet selection"""
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(StringIO(file_content.decode('utf-8')))
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                if sheet_name:
                    df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
                else:
                    df = pd.read_excel(io.BytesIO(file_content))
            elif filename.endswith('.json'):
                df = pd.read_json(StringIO(file_content.decode('utf-8')))
            else:
                return {"error": "Unsupported file format. Please upload CSV, Excel, or JSON files.", "success": False}
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            summary = {
                "columns": list(df.columns),
                "row_count": len(df),
                "numeric_columns": list(df.select_dtypes(include=['int64', 'float64']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object']).columns),
                "datetime_columns": list(df.select_dtypes(include=['datetime64']).columns),
                "boolean_columns": list(df.select_dtypes(include=['bool']).columns)
            }
            
            return {
                "data": df.to_json(orient='records'),
                "summary": summary,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def get_excel_sheets(file_content: bytes):
        """Get list of sheet names from Excel file"""
        try:
            xls = pd.ExcelFile(io.BytesIO(file_content))
            return {
                "sheets": xls.sheet_names,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def process_database_connection(connection_params):
        """Process database connection and get table information"""
        db_type = connection_params.get('db_type')
        host = connection_params.get('host')
        port = connection_params.get('port')
        database = connection_params.get('database')
        username = connection_params.get('username')
        password = connection_params.get('password')

        conn = None
        cursor = None
        try:
            if db_type == 'postgresql':
                conn = psycopg2.connect(host=host, port=port, database=database, user=username, password=password)
            elif db_type == 'mysql':
                conn = mysql.connector.connect(host=host, port=port, database=database, user=username, password=password)
            elif db_type == 'sqlite':
                conn = sqlite3.connect(database)
            elif db_type == 'sqlserver':
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={host},{port};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password}"
                )
                conn = pyodbc.connect(conn_str)
            else:
                return {"error": "Unsupported database type.", "success": False}

            cursor = conn.cursor()
            
            if db_type == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            elif db_type == 'postgresql':
                cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
            elif db_type == 'mysql':
                cursor.execute("SHOW TABLES;")
            elif db_type == 'sqlserver':
                cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")

            tables = []
            for row in cursor.fetchall():
                table_name = _validate_table_name(row[0])
                # For each table, get column names and a sample row count
                try:
                    df_sample = pd.read_sql(f"SELECT * FROM \"{table_name}\" LIMIT 10", conn)
                    columns = list(df_sample.columns)
                    # Attempt to get actual row count, or estimate if too slow
                    row_count_df = pd.read_sql(f"SELECT COUNT(*) FROM \"{table_name}\"", conn)
                    row_count = row_count_df.iloc[0, 0]
                    tables.append({
                        "name": table_name,
                        "columns": columns,
                        "row_count": row_count
                    })
                except Exception as col_e:
                    print(f"Could not get columns or row count for table {table_name}: {col_e}")
                    tables.append({
                        "name": table_name,
                        "columns": [],
                        "row_count": 0
                    })
            
            return {
                "tables": tables,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def fetch_database_table_data(connection_params, table_name: str):
        """Fetch data from a specified database table"""
        db_type = connection_params.get('db_type')
        host = connection_params.get('host')
        port = connection_params.get('port')
        database = connection_params.get('database')
        username = connection_params.get('username')
        password = connection_params.get('password')

        conn = None
        try:
            if db_type == 'postgresql':
                conn = psycopg2.connect(host=host, port=port, database=database, user=username, password=password)
            elif db_type == 'mysql':
                conn = mysql.connector.connect(host=host, port=port, database=database, user=username, password=password)
            elif db_type == 'sqlite':
                conn = sqlite3.connect(database)
            elif db_type == 'sqlserver':
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={host},{port};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password}"
                )
                conn = pyodbc.connect(conn_str)
            else:
                return {"error": "Unsupported database type.", "success": False}

            table_name = _validate_table_name(table_name)
            df = pd.read_sql(f"SELECT * FROM \"{table_name}\"", conn)
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            summary = {
                "columns": list(df.columns),
                "row_count": len(df),
                "numeric_columns": list(df.select_dtypes(include=['int64', 'float64']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object']).columns),
                "datetime_columns": list(df.select_dtypes(include=['datetime64']).columns),
                "boolean_columns": list(df.select_dtypes(include=['bool']).columns)
            }
            
            return {
                "data": df.to_json(orient='records'),
                "summary": summary,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
        finally:
            if conn:
                conn.close()
