import os
from urllib.parse import quote_plus

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()
_engine = None

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def _build_sqlalchemy_url():
    db_name = os.getenv("DB_NAME")
    user = quote_plus(os.getenv("DB_USER", ""))
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(_build_sqlalchemy_url(), pool_pre_ping=True)
    return _engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db(create_tables=True, create_views=True):
    from schema import create_views as create_db_views

    engine = get_engine()
    if create_tables:
        Base.metadata.create_all(bind=engine)
    if create_views:
        create_db_views(engine)
