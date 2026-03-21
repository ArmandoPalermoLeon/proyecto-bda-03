import psycopg2
import psycopg2.extras
from flask import g, current_app


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
            dbname=current_app.config["DB_NAME"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
        )
        g.db.autocommit = False
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=None, fetch="all"):
    conn = get_db()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params or ())
        if fetch == "one":
            return cur.fetchone()
        return cur.fetchall()


def execute(sql, params=None):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_app(app):
    import os
    app.config["DB_HOST"]     = os.getenv("DB_HOST",     "localhost")
    app.config["DB_PORT"]     = os.getenv("DB_PORT",     "5432")
    app.config["DB_NAME"]     = os.getenv("DB_NAME",     "alzheimer_db")
    app.config["DB_USER"]     = os.getenv("DB_USER",     "postgres")
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "")
    app.teardown_appcontext(close_db)
