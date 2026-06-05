import os
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())  # finds the .env at the project root

password = os.environ["MSSQL_SA_PASSWORD"]
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=fleetfix;"
    f"UID=sa;PWD={password};"
    "TrustServerCertificate=yes;"
)
url = f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"
engine = create_engine(url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)