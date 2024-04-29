import json
import os
import logging
import re
import pyodbc
from promptflow import tool

# Configure logging to use the level from PF_LOGGING_LEVEL or default to WARNING
@tool
def my_python_tool(sql_dict, user_input):
    # SQL query execution
    server = 'gen-ai-poc-db.database.windows.net'
    database = 'gen-ai-poc'
    username = 'test'
    password = 'Tyrannausaurus_1234!'
    driver= '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()

    # create_table_sql = f"CREATE TABLE [current_chat_history] (question VARCHAR(MAX));"
    insert_sql = "INSERT INTO current_chat_history ([question]) VALUES (?);"

    # Parse the outer JSON
    num_products = re.findall(r"'num_products'\:\s*(\d+)", str(sql_dict))
    if len(num_products) > 0:
        extracted_num = int(num_products[0])
        cursor.execute(insert_sql, [user_input])
        conn.commit()
        if extracted_num <= 50 and extracted_num != 0:
            conn.commit()
            # close connection
            cursor.close()
            conn.close()
            return 1
    else:
        if chat_history == []:
            cursor.execute(insert_sql, [user_input])
            conn.commit()
    # close connection
    cursor.close()
    conn.close()
    return 0