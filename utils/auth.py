import os
import json
import logging
import asyncio
from datetime import datetime

from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import (
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
    SessionPasswordNeededError,
)

from .file_utils import read_session_info, read_2fa_password


async def handle_session(folder):
    session_file, json_file = None, None
    for file in os.listdir(folder):
        if file.endswith(".session"):
            session_file = os.path.join(folder, file)
        elif file.endswith(".json"):
            json_file = os.path.join(folder, file)

    if not session_file or not json_file:
        logging.error(f"Папка {folder} пропущена из-за отсутствия необходимых файлов.")
        return

    session_info = read_session_info(json_file)
    two_fa_password = read_2fa_password(folder)

    try:
        client = TelegramClient(
            session=session_file,
            api_id=session_info["app_id"],
            api_hash=session_info["app_hash"],
        )
        await client.connect()

        if not await client.is_user_authorized():
            try:
                await client.send_code_request(session_info["phone"])
                await client.sign_in(session_info["phone"])
            except SessionPasswordNeededError:
                if two_fa_password:
                    await client.sign_in(password=two_fa_password)
                    logging.info(
                        f"Сессия {session_file} запросила 2FA, 2FA введен успешно"
                    )
                else:
                    logging.error(
                        f"Сессия {session_file} запросила 2FA, но пароль не найден в twoFA.txt. Пропуск сессии."
                    )
                    return

        logging.info(
            f"Успешно подключились к сессии: {session_info.get('first_name', '')} {session_info.get('last_name', '')}"
        )

        while True:
            logging.info(
                f"{session_info.get('first_name', '')} {session_info.get('last_name', '')} онлайн {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await asyncio.sleep(10)

    except PhoneNumberBannedError:
        logging.error(
            f"Сессия {session_file} пропущена из-за блокировки номера. Начинаем удаление..."
        )
        os.remove(session_file)  # Удаление файла сессии
        if os.path.exists(json_file):
            os.remove(json_file)  # Удаление соответствующего JSON файла
        if os.path.exists(os.path.join(folder, "twoFA.txt")):
            os.remove(os.path.join(folder, "twoFA.txt"))  # Удаление файла twoFA
    except PhoneNumberInvalidError:
        logging.error(
            f"Сессия {session_file} пропущена из-за невалидности номера. Начинаем удаление..."
        )
        os.remove(session_file)  # Удаление файла сессии
        if os.path.exists(json_file):
            os.remove(json_file)  # Удаление соответствующего JSON файла
        if os.path.exists(os.path.join(folder, "twoFA.txt")):
            os.remove(os.path.join(folder, "twoFA.txt"))  # Удаление файла twoFA
    except Exception as e:
        logging.error(f"An error occurred: {e}")
