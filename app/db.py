import psycopg2
import os
from typing import Dict, List
from dotenv import load_dotenv
load_dotenv()


# DB connection config (set using environment variables)
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "langgraph_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def fetch_customer_profile(customer_id: str) -> Dict:
    query = "SELECT * FROM customers WHERE customer_id = %s"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (customer_id,))
            row = cur.fetchone()
            if not row:
                return {}
            colnames = [desc[0] for desc in cur.description]
            return dict(zip(colnames, row))

def fetch_customer_activities(customer_id: str) -> List[Dict]:
    query = "SELECT * FROM activities WHERE customer_id = %s"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (customer_id,))
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return [dict(zip(colnames, row)) for row in rows]
