from promptflow import tool
import pyodbc

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
def my_python_tool(chat_input, chat_history):
    table_name = 'current_chat_history'

    # connect to Azure sql database
    server = 'gen-ai-poc-db.database.windows.net'
    database = 'gen-ai-poc'
    username = 'test'
    password = 'Tyrannausaurus_1234!'
    driver= '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()
    exists = check_table_exists(cursor, table_name)
    previous_history = []

    if exists == 1 and chat_history == []:
         # Drop Table if exists and continue work with Table1
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        cursor.commit()

        create_table_sql = f"CREATE TABLE {table_name} ([question] VARCHAR(MAX));"
        cursor.execute(create_table_sql)
        conn.commit()  # Commit the creation of the table if it's newly created

        # close connection
        cursor.close()
        conn.close()

    elif exists == 1 and chat_history != []:
        all_select_sql = f"""SELECT * FROM [{table_name}];"""
        cursor.execute(all_select_sql)
        previous_history = cursor.fetchall()
        previous_history = [''.join(hist) for hist in previous_history]
        # close connection
        cursor.close()
        conn.close()
    
    else:
        create_table_sql = f"CREATE TABLE {table_name} ([question] VARCHAR(MAX));"
        cursor.execute(create_table_sql)
        conn.commit()  # Commit the creation of the table if it's newly created
        # close connection
        cursor.close()
        conn.close()
    return str(chat_input) + ' \n'.join(previous_history)