import os
def create_table_from_csv(conn, file_path: str, table_name: str, delimiter: str = '|', encoding: str = "utf-8"):
    """
    Create a table on DuckDB
    """
    print(f"Processing '{os.path.basename(file_path)}': Table='{table_name}', Encoding='{encoding}', Delim='{delimiter}'")
    try:
        conn.sql(f"""
                CREATE OR REPLACE TEMP TABLE "{table_name}" AS
                (SELECT * FROM 
                read_csv('{file_path}',
                delim='{delimiter}',
                encoding='{encoding}',
                header=true,
                auto_detect=true
                ) LIMIT 1000)
                """)
        print(f"Create Table Successful '{table_name}' .")
        print(conn.sql(f'SELECT * FROM "{table_name}" LIMIT 3'))
    except Exception as e:
        print(f"ERROR Create Table doesnt work '{table_name}': {e}")