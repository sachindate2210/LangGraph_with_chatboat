import psycopg2

from config.db_config import DB_CONFIG


def save_memory(session_id, memory):

    conn = psycopg2.connect(**DB_CONFIG)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO agent_memory
        (session_id, memory)

        VALUES (%s, %s)
        """,
        (
            str(session_id),
            memory
        )
    )

    conn.commit()

    cursor.close()
    conn.close()


def retrieve_memory():

    conn = psycopg2.connect(**DB_CONFIG)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT memory
        FROM agent_memory
        ORDER BY id DESC
        LIMIT 5
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    memories = [row[0] for row in rows]

    return "\n".join(memories)