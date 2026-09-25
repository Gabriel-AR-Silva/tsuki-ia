from app.memory.database import get_connection, initialize_database


class MemoryRepository:
    def __init__(self):
        initialize_database()

    def save(self, content: str) -> int:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO memories (content)
                VALUES (?)
                """,
                (content,),
            )

            connection.commit()
            return int(cursor.lastrowid)

    def list_all(self) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, content, created_at
                FROM memories
                ORDER BY id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def search(self, query: str, limit: int = 5) -> list[dict]:
        pattern = f"%{query}%"

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, content, created_at
                FROM memories
                WHERE content LIKE ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (pattern, limit),
            ).fetchall()

        return [dict(row) for row in rows]

    def delete(self, memory_id: int) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE id = ?
                """,
                (memory_id,),
            )

            connection.commit()
            return cursor.rowcount > 0
