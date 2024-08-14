import os
import json
import logging
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import (
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.channels import (
    JoinChannelRequest,
    EditAdminRequest,
    UpdateUsernameRequest,
)
from telethon.tl.types import ChatAdminRights
from datetime import datetime
import random
import string

# Настройка логирования для вывода в консоль
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(asctime)s - %(message)s"
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


def read_channel_link():
    channel_file = (
        "/Users/a5555/Documents/developers/clients/brodyaga/LinkSoft/channel.txt"
    )
    if os.path.exists(channel_file):
        with open(channel_file, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None


def generate_random_username():
    return "".join(random.choices(string.ascii_letters + string.digits, k=13))


async def keep_alive(client, start_time):
    while True:
        elapsed_time = datetime.now() - start_time
        elapsed_seconds = int(elapsed_time.total_seconds())
        elapsed_minutes, elapsed_seconds = divmod(elapsed_seconds, 60)
        print(
            f"Аккаунт онлайн уже {elapsed_minutes} минут(ы) и {elapsed_seconds} секунд(ы)"
        )
        await asyncio.sleep(10)


async def join_channel_if_needed(client, channel_link):
    if channel_link:
        try:
            entity = await client.get_entity(channel_link)
            await client(JoinChannelRequest(entity))
            logging.info(f"Успешно вступили в канал: {channel_link}")
        except Exception as e:
            logging.error(f"Не удалось вступить в канал {channel_link}. Ошибка: {e}")


async def change_username_and_transfer_admin(
    client, channel_link, next_client_info, me
):
    new_username = generate_random_username()
    try:
        entity = await client.get_entity(channel_link)
        await client(UpdateUsernameRequest(channel=entity, username=new_username))
        logging.info(f"[{me.username}] Username канала изменен на: {new_username}")

        if next_client_info:
            await client(
                EditAdminRequest(
                    channel=entity,
                    user_id=next_client_info["phone"],
                    admin_rights=ChatAdminRights(
                        change_info=True,
                        post_messages=True,
                        edit_messages=True,
                        delete_messages=True,
                        ban_users=True,
                        invite_users=True,
                        pin_messages=True,
                        add_admins=True,
                        anonymous=False,
                        manage_call=True,
                    ),
                    rank="admin",
                )
            )
            logging.info(
                f"[{me.username}] Права администратора переданы сессии: {next_client_info['phone']}"
            )
    except Exception as e:
        logging.error(
            f"[{me.username}] Ошибка при изменении username или передаче прав: {e}"
        )


async def handle_session(folder, valid_count, channel_link, next_client_info):
    session_file = None
    json_file = None
    for file in os.listdir(folder):
        if file.endswith(".session"):
            session_file = os.path.join(folder, file)
        elif file.endswith(".json"):
            json_file = os.path.join(folder, file)

    if not session_file or not json_file:
        print(f"Папка {folder} пропущена из-за отсутствия необходимых файлов.")
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
                    print(f"Сессия {session_file} запросила 2FA, 2FA введен успешно")
                else:
                    print(
                        f"Сессия {session_file} запросила 2FA, но пароль не найден в twoFA.txt. Пропуск сессии."
                    )
                    return

        print(
            f"Успешно подключились к сессии: {session_info.get('first_name', '')} {session_info.get('last_name', '')}"
        )

        # Получение имени пользователя
        me = await client.get_me()
        print(f"Успешный вход: {me.first_name} {me.last_name}")
        valid_count.append(1)  # Добавление в список для подсчета валидных сессий

        # Проверка и вступление в канал, если необходимо
        await join_channel_if_needed(client, channel_link)

        # Запуск keep_alive задачи
        start_time = datetime.now()
        asyncio.create_task(keep_alive(client, start_time))

        # Изменение username и передача прав администратора
        while True:
            await change_username_and_transfer_admin(
                client, channel_link, next_client_info, me
            )
            await asyncio.sleep(60)  # Ожидание 60 секунд перед следующим изменением
            await asyncio.sleep(600)  # Затишье на 600 секунд

    except PhoneNumberBannedError:
        print(
            f"Сессия {session_file} пропущена из-за блокировки номера. Начинаем удаление..."
        )
        os.remove(session_file)  # Удаление файла сессии
        if os.path.exists(json_file):
            os.remove(json_file)  # Удаление соответствующего JSON файла
        if os.path.exists(os.path.join(folder, "twoFA.txt")):
            os.remove(os.path.join(folder, "twoFA.txt"))  # Удаление файла twoFA
    except PhoneNumberInvalidError:
        print(
            f"Сессия {session_file} пропущена из-за невалидности номера. Начинаем удаление..."
        )
        os.remove(session_file)  # Удаление файла сессии
        if os.path.exists(json_file):
            os.remove(json_file)  # Удаление соответствующего JSON файла
        if os.path.exists(os.path.join(folder, "twoFA.txt")):
            os.remove(os.path.join(folder, "twoFA.txt"))  # Удаление файла twoFA
    except Exception as e:
        print(f"An error occurred: {e}")


async def main(session_folder):
    session_folders = [
        os.path.join(session_folder, f)
        for f in os.listdir(session_folder)
        if os.path.isdir(os.path.join(session_folder, f))
    ]
    if len(session_folders) == 0:
        print("Ошибка: в выбранной папке нет папок сессий.")
        return

    valid_count = []
    channel_link = read_channel_link()

    tasks = []

    for i, folder in enumerate(session_folders):
        print(f"Подключаемся к сессии в папке: {folder}")

        next_client_info = None
        if i < len(session_folders) - 1:
            next_folder = session_folders[i + 1]
            next_json_file = [
                f for f in os.listdir(next_folder) if f.endswith(".json")
            ][0]
            next_client_info = read_session_info(
                os.path.join(next_folder, next_json_file)
            )

        tasks.append(
            asyncio.create_task(
                handle_session(folder, valid_count, channel_link, next_client_info)
            )
        )

    await asyncio.gather(*tasks)

    print(f"Удалено {len(session_folders) - len(valid_count)} сессий.")
    print(f"Валидных сессий: {len(valid_count)}")


# Пример вызова основной функции
session_folder = "session"

asyncio.run(main(session_folder))
