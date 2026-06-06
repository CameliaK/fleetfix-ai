import os
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())  # finds the .env at the project root
password = os.getenv("MSSQL_SA_PASSWORD")

db_host = os.environ.get("DB_HOST", "localhost,1433")
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={db_host};"
    "DATABASE=fleetfix;"
    f"UID=sa;PWD={password};"
    "TrustServerCertificate=yes;"
)
url = f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"
engine = create_engine(url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)