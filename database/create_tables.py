import psycopg2
from config.db_config import DB_CONFIG

def create_tables():

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_sessions (
        id SERIAL PRIMARY KEY,
        session_id UUID,
        user_input TEXT,
        final_response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_steps (
        id SERIAL PRIMARY KEY,
        session_id UUID,
        step_number INT,
        stage TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # MEMORY TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_memory (

        id SERIAL PRIMARY KEY,

        session_id UUID,

        memory TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
            
    conn.commit()

    cursor.close()
    conn.close()