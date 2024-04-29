from promptflow import tool
import pyodbc
import pandas as pd
import numpy as np

def df_from_extracted_products(rows, cursor):
    # Fetch all rows, and convert each row to a list
    list_rows = [list(row) for row in rows]
    # Fetch column names from cursor description
    columns = [desc[0] for desc in cursor.description]
    # Create DataFrame using the rows and column names
    df = pd.DataFrame(list_rows, columns=columns)
    return df

def not_unique_columns(rows, cursor):
    # Create dataset from exctacted rows
    df = df_from_extracted_products(rows, cursor)
    # Dictionary to hold columns with their non-unique values
    variation_dict = {}
    # Analyze the DataFrame to find columns with different values and list their unique values
    for col in df.columns:
        if df[col].nunique() > 1:
            # Store unique values in a set for each column with more than one unique value
            variation_dict[col] = set(df[col].dropna().unique())  # dropna() to avoid counting NaN as a value
    return variation_dict

def all_products_in_table(table_name, cursor, conn):
    all_sql = f"""SELECT * FROM [{table_name}];"""
    # Selecting all rows in table and count
    cursor.execute(all_sql)
    num_all = len(cursor.fetchall())
    conn.commit()
    return num_all

def pandas_to_sql_dtype(column):
    """Map pandas dtype to SQL data type."""
    if pd.api.types.is_integer_dtype(column):
        return 'INT'
    elif pd.api.types.is_float_dtype(column):
        return 'FLOAT'
    elif pd.api.types.is_datetime64_any_dtype(column):
        return 'DATETIME'
    elif pd.api.types.is_string_dtype(column):
        return 'VARCHAR(MAX)'  # You might want to specify a length limit based on your actual data
    else:
        return 'VARCHAR(MAX)'  # Default case if type is not matched

def create_table_from_df(df, table_name, cursor):
    """Create a SQL table from a DataFrame's schema."""
    columns_sql = []
    for col in df.columns:
        sql_type = pandas_to_sql_dtype(df[col])
        columns_sql.append(f"[{col}] {sql_type}")
    columns_sql = ",\n".join(columns_sql)
    create_table_sql = f"CREATE TABLE {table_name} (\n{columns_sql}\n);"

    # Drop old table if exists and create new table
    if table_name != 'product_catalogue_modified':
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        cursor.execute(create_table_sql)

def insert_data_from_df(df, table_name, cursor):
    """Insert data from DataFrame into SQL table."""
    placeholders = ', '.join(['?' for _ in range(len(df.columns))])
    columns = ', '.join([f"[{col}]" for col in df.columns])
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    for _, row in df.iterrows():
        cursor.execute(insert_sql, tuple(row))

def table_update(df, table_name, cursor, conn):
    # Create new table dynamically based on DataFrame schema
    create_table_from_df(df, table_name, cursor)
    conn.commit()  # Commit the creation of the table

    # Insert new rows dynamically
    insert_data_from_df(df, table_name, cursor)
    conn.commit()


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool

def query_execution(query1, query2, grounding):
    # checking if products num in Table2 is already satisfying and selecting all 
    if grounding:
        table_name = "product_catalogue_modified_cut"
        sql = f"""SELECT * FROM [{table_name}];"""
        
    # sql request creation for Table1
    elif query1:
        table_name = "product_catalogue_modified"
        sql = query1.split('```sql')[1].split('```')[0].replace(r'\n', '')

    # sql request creation for Table2
    else:
        table_name = "product_catalogue_modified_cut"
        sql = query2.split('```sql')[1].split('```')[0].replace(r'\n', '')

    # SQL query execution
    server = 'gen-ai-poc-db.database.windows.net'
    database = 'gen-ai-poc'
    username = 'test'
    password = 'Tyrannausaurus_1234!'
    driver= '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()

    # Number of extracted products
    num_products = len(rows)

    # Find column names where values are different
    not_unique = not_unique_columns(rows, cursor)

    # Check products amount in current table
    num_all = all_products_in_table(table_name, cursor, conn)

    # analyze extracted results and return data
    # IF number of extracted products is satisfying
    if num_products == 0:
        conn.commit()
        # close connection
        cursor.close()
        conn.close()
        return {'num_products': num_products, 'num_all': num_all, 'table_name': table_name, 'not_unique': not_unique, 'sql': sql, 'result': rows}
    
    elif num_products <= 200:
        table_name = "product_catalogue_modified_cut"
        df = df_from_extracted_products(rows, cursor)
        table_update(df, table_name, cursor, conn)
        # Commit the transactions and close the connection
        conn.commit()
        # close connection
        cursor.close()
        conn.close()
        return {'num_products': num_products, 'num_all': num_all, 'table_name': table_name, 'not_unique': not_unique, 'sql': sql, 'result': rows}

    # IF number of extracted products is still huge but less than previously extracted
    elif num_products < num_all:
        # Rewrite a Table2
        table_name = "product_catalogue_modified_cut"
        df = df_from_extracted_products(rows, cursor)
        table_update(df, table_name, cursor, conn)
        # Commit the transactions and close the connection
        conn.commit()
        # close connection
        cursor.close()
        conn.close()
        return {'num_products': num_products, 'num_all': num_all, 'table_name': table_name, 'not_unique': not_unique, 'sql': sql, 'result': rows[:10]}

    # Process any other case
    else:
        # Commit the transactions and close the connection
        conn.commit()
        # close connection
        cursor.close()
        conn.close()
        return {'num_products': num_products, 'num_all': num_all, 'table_name': table_name, 'not_unique': not_unique, 'sql': sql, 'result': rows[:10]}