import psycopg2
from config.db_config import DB_CONFIG

def save_session(session_id, user_input, final_response):

    conn = psycopg2.connect(**DB_CONFIG)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO agent_sessions
        (session_id, user_input, final_response)

        VALUES (%s, %s, %s)
        """,
        (
            str(session_id),
            user_input,
            final_response
        )
    )

    conn.commit()

    cursor.close()
    conn.close()