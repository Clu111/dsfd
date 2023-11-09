import sqlite3
from contextlib import contextmanager
from sqlite3 import Connection

import uvicorn
from fastapi import FastAPI

from routes.share import share_router
from settings import Settings

app = FastAPI(
    docs_url='/'
)

app.include_router(share_router, prefix='/file', tags=['file'])


@contextmanager
def connection_context():
    connection = sqlite3.connect('files_db.db')
    try:
        yield connection
    finally:
        connection.close()


if __name__ == '__main__':
    with connection_context() as connection:
        connection: Connection
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS FILES (
            file_uuid TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            original_file_name TEXT NOT NULL 
            )
            """
        )
        connection.commit()
    uvicorn.run('main:app', host='0.0.0.0', port=Settings.port, reload=True)