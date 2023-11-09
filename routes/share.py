import sqlite3
import uuid
from pathlib import Path
from sqlite3 import Connection
from typing import Union

from fastapi import APIRouter, Depends, UploadFile, Response
from starlette.responses import FileResponse

from settings import Settings

share_router = APIRouter()


def get_connection():
    """Функция получения подключения к БД."""
    connection = sqlite3.connect('files_db.db')
    try:
        yield connection
    finally:
        connection.close()


@share_router.get('/{file_uuid}')
def download_file(file_uuid: str, db: Connection = Depends(get_connection)):
    """Функция загрузки файла с сервера.

    :param file_uuid: идентификатор файла
    :param db: подключение к БД
    """
    cursor = db.cursor()
    cursor.execute('SELECT file_path, original_file_name FROM FILES WHERE file_uuid = ?', (file_uuid,))
    file_info = cursor.fetchone()
    if not file_info:
        return Response(status_code=404)
    return FileResponse(file_info[0], filename=file_info[1])


@share_router.post('/upload/')
def upload_file(file: UploadFile, db: Connection = Depends(get_connection)) -> str:
    """Функция загрузки файла на сервер.

    :param file: объект, содержащий данные о принимаемом файле.
    :param db: подключение к БД
    """

    file_uuid = uuid.uuid4()
    file_path = Path.cwd() / 'files_storage' / f'{file_uuid.hex}{Path(file.filename).suffix}'

    with file_path.open('wb') as disk_file:
        disk_file.write(file.file.read())
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO FILES (file_uuid, file_path, original_file_name) VALUES (?, ?, ?)',
        (file_uuid.hex, str(file_path), file.filename)
    )
    db.commit()
    return f'http://{Settings.domain}:{Settings.port}/file/{file_uuid.hex}'