from sqlalchemy import create_engine, MetaData
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ai_agent.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
meta = MetaData()

def get_engine():
    return engine
