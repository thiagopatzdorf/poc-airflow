"""Migrações pequenas, repetíveis e executadas com o dono do banco de negócio."""
from poc.process_store import _connect


def migrate() -> None:
    with _connect() as conn, conn.cursor() as cursor:
        cursor.execute("ALTER TABLE process_events ADD COLUMN IF NOT EXISTS event_key text")
        cursor.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS process_events_event_key_uidx
               ON process_events (event_key) WHERE event_key IS NOT NULL"""
        )


if __name__ == "__main__":
    migrate()
