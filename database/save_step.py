import psycopg2
from config.db_config import DB_CONFIG

def save_step(session_id, step_number, stage, content):

    conn = psycopg2.connect(**DB_CONFIG)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO agent_steps
        (session_id, step_number, stage, content)

        VALUES (%s, %s, %s, %s)
        """,
        (
            str(session_id),
            step_number,
            stage,
            content
        )
    )

    conn.commit()

    cursor.close()
    conn.close()