import os
import json
import logging
import asyncio
from datetime import datetime
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QFileDialog
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
            change_channel_username_periodically(client, channel, usernames, interval)
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


class AppWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Telegram Channel Bot")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QtWidgets.QVBoxLayout()

        self.session_folder_label = QtWidgets.QLabel("Папка сессий:")
        self.layout.addWidget(self.session_folder_label)

        self.session_folder_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.session_folder_input)

        self.session_folder_button = QtWidgets.QPushButton("Выбрать папку", self)
        self.session_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.session_folder_button)

        self.channel_username_label = QtWidgets.QLabel("Введите username канала:")
        self.layout.addWidget(self.channel_username_label)

        self.channel_username_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.channel_username_input)

        self.username_1_label = QtWidgets.QLabel("Введите первый username:")
        self.layout.addWidget(self.username_1_label)

        self.username_1_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.username_1_input)

        self.username_2_label = QtWidgets.QLabel("Введите второй username:")
        self.layout.addWidget(self.username_2_label)

        self.username_2_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.username_2_input)

        self.username_3_label = QtWidgets.QLabel("Введите третий username:")
        self.layout.addWidget(self.username_3_label)

        self.username_3_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.username_3_input)

        self.interval_label = QtWidgets.QLabel("Интервал смены username (сек):")
        self.layout.addWidget(self.interval_label)

        self.interval_input = QtWidgets.QSpinBox(self)
        self.interval_input.setRange(60, 3600)
        self.interval_input.setValue(600)
        self.layout.addWidget(self.interval_input)

        self.run_button = QtWidgets.QPushButton("Запустить", self)
        self.run_button.clicked.connect(self.run_bot)
        self.layout.addWidget(self.run_button)

        self.setLayout(self.layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выбрать папку сессий")
        if folder:
            self.session_folder_input.setText(folder)

    def run_bot(self):
        session_folder = self.session_folder_input.text()
        channel_username = self.channel_username_input.text()
        usernames = [
            self.username_1_input.text(),
            self.username_2_input.text(),
            self.username_3_input.text(),
        ]
        interval = self.interval_input.value()

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


def test():
    current_dir = os.getcwd()

    print(current_dir)

    # Добавляем папку "session" к пути
    session_path = os.path.join(current_dir, 'soft/session')

    print(session_path)
