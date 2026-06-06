import os
import psycopg
from psycopg.rows import dict_row
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _get_connstr() -> str:
    """Devuelve el connection string según el entorno."""
    try:
        cfg = st.secrets["database"]
        return (
            f"host={cfg['host']} port={cfg['port']} dbname={cfg['dbname']} "
            f"user={cfg['user']} password={cfg['password']} sslmode=require"
        )
    except (KeyError, AttributeError):
        return (
            f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT', 5432)} "
            f"dbname={os.getenv('DB_NAME', 'postgres')} user={os.getenv('DB_USER', 'postgres')} "
            f"password={os.getenv('DB_PASSWORD')} sslmode=require"
        )


def get_connection():
    return psycopg.connect(_get_connstr(), row_factory=dict_row)


def execute(sql: str, params=None, fetch: bool = False):
    with psycopg.connect(_get_connstr(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch:
                return cur.fetchall()


def executemany(sql: str, params_list: list):
    with psycopg.connect(_get_connstr()) as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, params_list)
