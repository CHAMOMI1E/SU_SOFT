import os
import json
import logging
import asyncio
import random
import string
import coloredlogs
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import (
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.account import UpdateUsernameRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerEmpty

# Настройка логирования для вывода в консоль
logger = logging.getLogger(__name__)
coloredlogs.install(
    level="INFO",
    logger=logger,
    fmt="%(asctime)s - %(asctime)s - %(levelname)s - %(message)s",
    level_styles={"info": {"color": "magenta"}},
)


def read_session_info(session_file):
    json_file = os.path.splitext(session_file)[0] + ".json"
    with open(json_file, "r", encoding="utf-8") as file:
        session_info = json.load(file)
    return session_info


def read_2fa_password(folder):
    two_fa_file = os.path.join(folder, "twoFA.txt")
    if os.path.exists(two_fa_file):
        with open(two_fa_file, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None


def generate_random_username():
    return "".join(random.choices(string.ascii_letters + string.digits, k=12))


async def perform_actions(client, me):
    while True:
        new_username = generate_random_username()
        try:
            await client(UpdateUsernameRequest(new_username))
            logger.info(
                f"[{me.first_name} {me.last_name}] Юзернейм изменен на: {new_username}"
            )
        except Exception as e:
            logger.error(
                f"[{me.first_name} {me.last_name}] Ошибка при смене юзернейма: {e}"
            )

        await asyncio.sleep(600)

        try:
            result = await client(
                GetDialogsRequest(
                    offset_date=None,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=10,
                    hash=0,
                )
            )
            logger.info(f"[{me.first_name} {me.last_name}] Получены диалоги")
        except Exception as e:
            logger.error(
                f"[{me.first_name} {me.last_name}] Ошибка при получении диалогов: {e}"
            )

        await asyncio.sleep(600)

        try:
            full_user = await client(GetFullUserRequest(me))
            logger.info(f"[{me.first_name} {me.last_name}] Получен профиль")
        except Exception as e:
            logger.error(
                f"[{me.first_name} {me.last_name}] Ошибка при получении профиля: {e}"
            )

        await asyncio.sleep(600)


def delete_folder(folder):
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        os.rmdir(folder)
        logger.info(f"Папка {folder} удалена.")
    except Exception as e:
        logger.error(f"Ошибка при удалении папки {folder}: {e}")


async def handle_session(folder):
    session_file = None
    json_file = None
    for file in os.listdir(folder):
        if file.endswith(".session"):
            session_file = os.path.join(folder, file)
        elif file.endswith(".json"):
            json_file = os.path.join(folder, file)

    if not session_file or not json_file:
        logger.warning(f"Папка {folder} пропущена из-за отсутствия необходимых файлов.")
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
                    logger.info(
                        f"Сессия {session_file} запросила 2FA, 2FA введен успешно"
                    )
                else:
                    logger.warning(
                        f"Сессия {session_file} запросила 2FA, но пароль не найден в twoFA.txt. Пропуск сессии."
                    )
                    delete_folder(folder)
                    return

        me = await client.get_me()
        logger.info(f"Успешно подключились к сессии: {me.first_name} {me.last_name}")

        asyncio.create_task(perform_actions(client, me))

        while True:
            await asyncio.sleep(60)

    except (PhoneNumberBannedError, PhoneNumberInvalidError) as e:
        logger.warning(
            f"Сессия {session_file} пропущена из-за ошибки: {e}. Начинаем удаление..."
        )
        delete_folder(folder)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        delete_folder(folder)


async def main(session_folder):
    session_folders = [
        os.path.join(session_folder, f)
        for f in os.listdir(session_folder)
        if os.path.isdir(os.path.join(session_folder, f))
    ]
    if len(session_folders) == 0:
        logger.error("Ошибка: в выбранной папке нет папок сессий.")
        return

    tasks = []

    for folder in session_folders:
        logger.info(f"Подключаемся к сессии в папке: {folder}")
        tasks.append(asyncio.create_task(handle_session(folder)))

    await asyncio.gather(*tasks)

    logger.info(f"Все сессии обработаны.")


session_folder = "session"

asyncio.run(main(session_folder))
