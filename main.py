import os
import psycopg2
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
app = FastAPI()


@app.get("/health")
async def health():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()

                return {
                    "status": "ok",
                    "msg": f"Successfully connected! Database version: {db_version}",
                }

    except Exception as error:
        return {"status": "not ok", "msg": f"Error connecting to PostgreSQL: {error}"}
