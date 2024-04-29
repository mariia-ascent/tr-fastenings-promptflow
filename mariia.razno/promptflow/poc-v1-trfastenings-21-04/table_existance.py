from promptflow import tool
import pyodbc
import pandas as pd

def check_table_exists(cursor, table_name):
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
def initial_querying(chat_history):
    table_name = 'product_catalogue_cut'

    # connect to Azure sql database
    server = 'gen-ai-poc-db.database.windows.net'
    database = 'gen-ai-poc'
    username = 'test'
    password = 'Tyrannausaurus_1234!'
    driver= '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()
    exists = check_table_exists(cursor, table_name)

    if exists == 1 and chat_history == []:
         # Drop Table if exists and continue work with Table1
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

        # close connection
        cursor.close()
        conn.close()
        return 0
    elif exists == 1 and chat_history != []:
        all_select_sql = f"""SELECT * FROM [{table_name}];"""
        cursor.execute(all_select_sql)
        num_all = len(cursor.fetchall())

        # close connection
        cursor.close()
        conn.close()
        
        if int(num_all) <= 50:
            return 2
        else:
            return 1
    else:
        return 0
