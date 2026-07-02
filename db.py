import duckdb
from pathlib import Path

DB_PATH = Path("data/fasting_tracker.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    return duckdb.connect(DB_PATH)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fasting_logs (
            id INTEGER,
            start_time TIMESTAMP,
            fasting_hours INTEGER,
            eating_hours INTEGER,
            target_end_time TIMESTAMP,
            actual_end_time TIMESTAMP,
            status VARCHAR,
            notes VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  )
    """)
    conn.close()

def insert_fast(start_time, fasting_hours, eating_hours, target_end_time, actual_end_time, status, notes):
    conn = get_connection()
    
    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM fasting_logs").fetchone()[0]

    conn.execute("""
        INSERT INTO fasting_logs (id, start_time, fasting_hours, eating_hours, target_end_time, actual_end_time, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [next_id, start_time, fasting_hours, eating_hours, target_end_time, actual_end_time, status, notes])

    conn.close()

def close_active_fast(actual_end_time):
    conn = get_connection()
    conn.execute("""
        UPDATE fasting_logs
        SET actual_end_time = ?, status = 'cerrado'
        WHERE status='activo'
    """, [actual_end_time])
    conn.close()

def get_logs():
    conn = get_connection()
    df = conn.execute("SELECT * FROM fasting_logs ORDER BY start_time DESC").df()
    conn.close()
    return df

def get_active_fast():
    conn = get_connection()
    df = conn.execute("SELECT * FROM fasting_logs WHERE status='activo' ORDER BY start_time DESC LIMIT 1").df()
    conn.close()
    return df