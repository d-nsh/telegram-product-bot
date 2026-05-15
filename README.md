# telegram-product-bot
# Telegram Bot for Product Photo Processing

Telegram-бот для автоматической обработки фотографий товаров.

## Возможности

- удаление фона с помощью AI (`rembg`)
- белый фон
- центрирование объекта
- создание изображения 1000x1000
- Telegram-интерфейс

## Технологии

- Python
- requests
- rembg
- Pillow
- Telegram Bot API

---

## Установка

### 1. Клонировать проект

```bash
git clone https://github.com/d-nsh/telegram-product-bot.git
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## Настройка токена

Создайте файл `.env`

Пример:

```env
BOT_TOKEN=your_telegram_token
```

---

## Запуск

```bash
python bot.py
```

---

## Как использовать

1. Запустить бота
2. Открыть бота в Telegram
3. Отправить фото товара
4. Получить изображение с удалённым фоном

---

## Пример результата

- исходное фото товара
- обработанное изображение на белом фоне

---

## Автор

Danish Khan
