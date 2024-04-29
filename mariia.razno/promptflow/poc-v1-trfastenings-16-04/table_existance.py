from promptflow import tool
import pyodbc
import pandas as pd

def check_table_exists(db_connection, table_name):
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = ?
    """, (table_name,))
    if cursor.fetchone()[0] == 1:
        return 1
    return 0

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def initial_querying() -> str:
    table_name = 'product_catalogue_modified_cut'

    # connect to Azure sql database
    server = 'gen-ai-poc-db.database.windows.net'
    database = 'gen-ai-poc'
    username = 'test'
    password = 'Tyrannausaurus_1234!'
    driver= '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    exists = check_table_exists(conn, table_name)

    # close connection
    conn.close()
    if exists == 1:
        all_select_sql = f"""SELECT * FROM [{table_name}];"""
        conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = conn.cursor()
        cursor.execute(all_select_sql)
        num_all = len(cursor.fetchall())

        # close connection
        cursor.close()
        conn.close()
        
        if int(num_all) <= 200:
            return 2
        else:
            return 1
    else:
        return 0
