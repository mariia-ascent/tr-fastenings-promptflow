from promptflow import tool
import pyodbc

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def initial_querying(generated_sql: str) -> str:
    sql = generated_sql.split('```sql')[1].split('```')[0].replace(r'\n', '')

    ##if sql is not empty
    if sql:
        # connect to Azure sql database
        server = 'gen-ai-poc-db.database.windows.net'
        database = 'gen-ai-poc'
        username = 'test'
        password = 'Tyrannausaurus_1234!'
        driver= '{ODBC Driver 17 for SQL Server}'
        conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = conn.cursor()
        
        cursor.execute(sql)
        rows = cursor.fetchall()

        # close connection
        cursor.close()
        conn.close()
            
        return {"raw_sql": generated_sql, "sql":sql, "result":rows[:10], 'num_results': len(rows)}
    
    return generated_sql