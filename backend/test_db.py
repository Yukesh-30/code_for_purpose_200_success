import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL')
engine = create_engine(url)

try:
    with engine.connect() as conn:
        res = conn.execute(text("show default_transaction_read_only;"))
        print("default_transaction_read_only:", res.fetchone()[0])
        
        res = conn.execute(text("show transaction_read_only;"))
        print("transaction_read_only:", res.fetchone()[0])
        
        print("Attempting to insert into chat_messages...")
        # Try a dummy insert or just check if we can create a temp table
        conn.execute(text("CREATE TEMP TABLE test_write (id int);"))
        conn.execute(text("INSERT INTO test_write VALUES (1);"))
        print("Write successful in temp table")
        conn.commit()
except Exception as e:
    print("Error during DB test:", e)
