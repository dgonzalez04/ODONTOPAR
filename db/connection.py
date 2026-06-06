import os
import psycopg2
import psycopg2.extras
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    try:
        cfg = st.secrets["database"]
        return psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            dbname=cfg["dbname"],
            user=cfg["user"],
            password=cfg["password"],
            sslmode="require",
        )
    except (KeyError, AttributeError):
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require",
        )


def execute(sql: str, params=None, fetch: bool = False):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                if fetch:
                    return cur.fetchall()
    finally:
        conn.close()


def executemany(sql: str, params_list: list):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(cur, sql, params_list)
    finally:
        conn.close()
