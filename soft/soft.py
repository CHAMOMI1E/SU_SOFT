import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Coroutine

from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import (
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.channels import (
    JoinChannelRequest,
    UpdateUsernameRequest,
    EditAdminRequest,
)
from telethon.tl.types import ChatAdminRights

from config.settings import CHANNEL
from db.requests.link import get_first_url, get_next_url

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


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


async def keep_alive(client, start_time, username):
    while True:
        elapsed_time = datetime.now() - start_time
        elapsed_seconds = int(elapsed_time.total_seconds())
        elapsed_minutes, elapsed_seconds = divmod(elapsed_seconds, 60)
        print(
            f"[{username}] онлайн уже {elapsed_minutes} минут(ы) и {elapsed_seconds} секунд(ы)"
        )
        await asyncio.sleep(10)


async def transfer_channel_ownership(client, channel):
    async for user in client.iter_participants(channel):
        if not user.bot:
            new_admin_rights = ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=True,
                anonymous=True,
                manage_call=True,
            )
            try:
                await client(
                    EditAdminRequest(
                        channel=channel,
                        user_id=user.id,
                        admin_rights=new_admin_rights,
                        rank="Owner",
                    )
                )
                print(f"Передал(а) права {user.username or user.id}")
                break
            except Exception as e:
                pass


async def change_channel_username_periodically(client, channel):
    new_username = await get_first_url()
    while True:
        try:
            if new_username:
                await client(UpdateUsernameRequest(channel=channel, username=new_username.url))
                print(f"Сменен username канала на {new_username}")
                new_username = await get_next_url(new_username.id)
            else:
                new_username = await get_first_url()
                print("Нет ссылок для смены")
        except Exception as e:
            print(e)
        await asyncio.sleep(900)


async def handle_session(folder, channel_username):
    session_file = None
    json_file = None
    for file in os.listdir(folder):
        if file.endswith(".session"):
            session_file = os.path.join(folder, file)
        elif file.endswith(".json"):
            json_file = os.path.join(folder, file)

    if not session_file and not json_file:
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

        me = await client.get_me()
        username = me.username if me.username else f"{me.first_name} {me.last_name}"
        print(f"Успешный вход: {username}")

        # Вступление в канал
        await client(JoinChannelRequest(channel_username))
        print(f"{username} вступил в канал {channel_username}")

        channel = await client.get_entity(channel_username)

        start_time = datetime.now()
        asyncio.create_task(keep_alive(client, start_time, username))

        asyncio.create_task(
            change_channel_username_periodically(client, channel)
        )

    except PhoneNumberBannedError:
        print(f"Сессия {session_file} пропущена из-за блокировки номера.")
    except PhoneNumberInvalidError:
        print(f"Сессия {session_file} пропущена из-за невалидности номера.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def main(session_folder, channel_username):
    session_folders = [
        os.path.join(session_folder, f)
        for f in os.listdir(session_folder)
        if os.path.isdir(os.path.join(session_folder, f))
    ]
    if len(session_folders) == 0:
        print("Ошибка: в выбранной папке нет папок сессий.")
        return

    tasks = []

    for folder in session_folders:
        print(f"Подключаемся к сессии в папке: {folder}")
        tasks.append(
            asyncio.create_task(
                handle_session(folder, channel_username)
            )
        )

    await asyncio.gather(*tasks)

    while True:
        await asyncio.sleep(10)


def start_soft():
    session_folder = os.path.join(os.getcwd(), 'soft/session')
    channel_username = CHANNEL
    asyncio.run(main(session_folder, channel_username))


if __name__ == "__main__":
    # app = QtWidgets.QApplication([])
    # window = AppWindow()
    # window.show()
    # app.exec()
    current_dir = os.getcwd()

    print(current_dir)

    # Добавляем папку "session" к пути
    session_path = os.path.join(current_dir, 'session')

    print(session_path)
