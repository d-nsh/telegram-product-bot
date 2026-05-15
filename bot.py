# -*- coding: utf-8 -*-

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from image_processing import make_product_card


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Не найден BOT_TOKEN. Проверьте файл .env")

API_URL = f"https://api.telegram.org/bot{TOKEN}"

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


def tg_get(method, params=None, retries=3):
    for attempt in range(retries):
        try:
            return requests.get(
                f"{API_URL}/{method}",
                params=params,
                timeout=120
            ).json()
        except Exception as e:
            print(f"Ошибка GET {method}, попытка {attempt + 1}: {e}")
            time.sleep(5)

    return {"ok": False, "result": []}


def tg_post(method, data=None, files=None, retries=3):
    for attempt in range(retries):
        try:
            return requests.post(
                f"{API_URL}/{method}",
                data=data,
                files=files,
                timeout=120
            ).json()
        except Exception as e:
            print(f"Ошибка POST {method}, попытка {attempt + 1}: {e}")
            time.sleep(5)

    return {"ok": False}


def send_message(chat_id, text):
    tg_post("sendMessage", data={"chat_id": chat_id, "text": text})


def send_photo(chat_id, image_path, caption="Готово ✅"):
    with open(image_path, "rb") as photo:
        tg_post(
            "sendPhoto",
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": photo}
        )


def download_file(file_id, save_path):
    print("Получаю путь к файлу...")

    file_info = tg_get("getFile", params={"file_id": file_id})

    if not file_info.get("ok"):
        raise RuntimeError("Не удалось получить файл от Telegram")

    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    print("Скачиваю файл...")

    response = requests.get(file_url, timeout=120)
    response.raise_for_status()

    with open(save_path, "wb") as file:
        file.write(response.content)


def process_update(update):
    if "message" not in update:
        return

    message = update["message"]
    chat_id = message["chat"]["id"]

    if "text" in message and message["text"] == "/start":
        send_message(
            chat_id,
            "Привет! Отправь мне фото товара, а я удалю фон и сделаю изображение на белом фоне."
        )
        return

    if "photo" in message:
        try:
            print("Получено фото")
            send_message(chat_id, "Фото получил. Обрабатываю...")

            user_id = message["from"]["id"]
            photo = message["photo"][-1]
            file_id = photo["file_id"]

            input_path = TEMP_DIR / f"{user_id}_input.jpg"
            output_path = TEMP_DIR / f"{user_id}_card.jpg"

            print("Скачиваю фото...")
            download_file(file_id, input_path)

            print("Удаляю фон и создаю изображение...")
            make_product_card(input_path, output_path)

            print("Отправляю результат...")
            send_photo(chat_id, output_path)

            print("Готово")
        except Exception as e:
            print("Ошибка обработки фото:", e)
            send_message(
                chat_id,
                "Не получилось обработать фото. Попробуйте отправить другое изображение."
            )

        return

    send_message(chat_id, "Отправьте фото товара, и я сделаю изображение на белом фоне.")


def main():
    print("Бот запущен. Жду сообщения...")

    offset = None

    while True:
        try:
            updates = tg_get(
                "getUpdates",
                params={"timeout": 120, "offset": offset}
            )

            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                process_update(update)

        except Exception as e:
            print("Ошибка основного цикла:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()