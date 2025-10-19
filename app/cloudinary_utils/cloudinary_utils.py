"""
Модуль `cloudinary_utils.py`

Забезпечує завантаження файлів користувачів (наприклад, аватарів)
у хмарне сховище **Cloudinary**.

Cloudinary використовується для безпечного зберігання та
отримання публічних посилань на зображення.

Перед використанням необхідно встановити змінні середовища:

- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
"""

import os
import cloudinary
import cloudinary.uploader

# ---------- Конфігурація Cloudinary ----------

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_avatar_file(file) -> str:
    """
    Завантажує аватар користувача у Cloudinary та повертає посилання.

    Args:
        file: Об’єкт файлу (наприклад, `UploadFile.file` із FastAPI),
              який потрібно завантажити.

    Returns:
        str: Безпечне (`https`) публічне посилання на завантажене зображення.

    Example:
        >>> with open("avatar.png", "rb") as f:
        ...     url = upload_avatar_file(f)
        ...     print(url)
        'https://res.cloudinary.com/.../avatar.png'

    Notes:
        - Файли зберігаються у папці **avatars**.
        - Якщо файл уже існує, він буде **перезаписаний** (`overwrite=True`).
    """
    # file is a SpooledTemporaryFile or file-like (fastapi UploadFile)
    result = cloudinary.uploader.upload(file, folder="avatars", overwrite=True)
    return result.get("secure_url")