import psycopg2

from langchain_core.tools import Tool
from config.db_config import DB_CONFIG

def query_db(query):

    conn = psycopg2.connect(**DB_CONFIG)

    cursor = conn.cursor()

    cursor.execute(query)

    try:
        result = cursor.fetchall()

    except:
        result = "Executed"

    conn.commit()

    cursor.close()
    conn.close()

    return str(result)

database_tool = Tool(
    name="Database",
    func=query_db,
    description="Execute PostgreSQL query"
)