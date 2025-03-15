import time
import psutil
import speedtest
from aiogram import Bot, types
from datetime import datetime
from loguru import logger

MB_FACTOR = 1024 * 1024  # Константа для конвертації байтів у МБ
AVERAGE_PACKET_SIZE = 1500  # Середній розмір одного мережевого пакета (в байтах)

STARTUP_TIME = None

def initialize_startup_time():
    """
    Ініціалізує час запуску бота, якщо він ще не заданий.
    """
    global STARTUP_TIME
    if STARTUP_TIME is None:
        STARTUP_TIME = datetime.now()

async def get_uptime() -> str:
    """
    Повертає рядок з інформацією про те, скільки часу бот перебуває онлайн.
    """
    global STARTUP_TIME
    if STARTUP_TIME is None:
        initialize_startup_time()
        return "Бот щойно запустився!"
    
    now = datetime.now()
    uptime_delta = now - STARTUP_TIME
    
    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days} дн., {hours} год., {minutes} хв., {seconds} сек."

async def get_server_info() -> dict:
    """
    Збирає та повертає інформацію про систему: 
    • кількість відправлених/отриманих пакетів,
    • використання оперативної пам’яті,
    • загальний обсяг оперативної пам’яті,
    • завантаження CPU.
    
    Повертається словник з відповідними ключами.
    """
    net_io = psutil.net_io_counters(pernic=True)
    
    if not net_io:
        raise ValueError("Немає доступних мережевих інтерфейсів для відстеження.")

    # Беремо перший доступний інтерфейс
    interface = next(iter(net_io))
    io_data = net_io[interface]

    return {
        "packets_sent": io_data.packets_sent,
        "packets_recv": io_data.packets_recv,
        "ram_used": psutil.virtual_memory().used,
        "ram_total": psutil.virtual_memory().total,
        "cpu_load": psutil.cpu_percent()
    }

async def convert_packets_to_mb(sent_packets: int, received_packets: int) -> tuple[float, float]:
    """
    Перетворює кількість пакетів на приблизний обсяг переданих даних (у МБ).
    Використовується усереднене значення розміру одного пакета (AVERAGE_PACKET_SIZE).
    """
    sent_bytes = sent_packets * AVERAGE_PACKET_SIZE
    received_bytes = received_packets * AVERAGE_PACKET_SIZE

    sent_mb = sent_bytes / MB_FACTOR
    received_mb = received_bytes / MB_FACTOR
    
    return sent_mb, received_mb

async def get_internet_speed() -> tuple[float, float, float]:
    """
    Виконує перевірку швидкості інтернету за допомогою speedtest.
    Повертає трійку значень:
    (швидкість завантаження (Мбіт/с), швидкість вивантаження (Мбіт/с), пінг (мс)).
    """
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000   # біт/с -> Мбіт/с
    upload_speed = st.upload() / 1_000_000       # біт/с -> Мбіт/с
    ping = st.results.ping                       # мс
    return download_speed, upload_speed, ping

async def ping_command(message: types.Message, bot: Bot):
    """
    Команда /ping для телеграм-бота, яка:
    • Вимірює час відповіді бота (за допомогою повідомлення Pong).
    • Збирає інформацію про використання ресурсів сервера (RAM, CPU).
    • Виводить приблизний обсяг переданих та отриманих даних (орієнтуючись на кількість пакетів).
    • Виконує Speedtest для перевірки швидкості інтернет-з’єднання та оновлює повідомлення з результатами.
    """
    try:
        # Замір часу відповіді бота
        start_time = time.time()
        temp_message = await message.answer("🏓 Pong")
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000

        # Отримуємо інформацію про сервер
        server_info = await get_server_info()
        
        # Конвертуємо кількість пакетів у МБ
        sent_mb, received_mb = await convert_packets_to_mb(
            server_info["packets_sent"], 
            server_info["packets_recv"]
        )
        
        # Формуємо попереднє повідомлення з базовою інформацією
        initial_text = (
            f"🏓 <b>Pong!</b>\n\n"
            f"Час відповіді бота: <code>{response_time_ms:.2f} мс</code>\n"
            f"Передано даних: <code>≈{sent_mb:.2f} МБ</code>\n"
            f"Отримано даних: <code>≈{received_mb:.2f} МБ</code>\n"
            f"Бот працює: <code>{await get_uptime()}</code>\n\n"
            f"💡 <b>Інформація про сервер</b>:\n"
            f"ОП: <code>{server_info['ram_used'] // MB_FACTOR} / {server_info['ram_total'] // MB_FACTOR} МБ</code>\n"
            f"CPU: <code>{server_info['cpu_load']:.2f}%</code>"
        )

        # Відправляємо попередній результат
        info_message = await message.answer(initial_text)
        # Прибираємо тимчасове повідомлення "Вимірюю пінг..."
        await bot.delete_message(chat_id=message.chat.id, message_id=temp_message.message_id)

        # Виконуємо Speedtest
        download_speed, upload_speed, ping = await get_internet_speed()

        # Оновлене повідомлення з додатковою інформацією про інтернет
        final_text = (
            f"🏓 <b>Pong!</b>\n\n"
            f"Час відповіді бота: <code>{response_time_ms:.2f} мс</code>\n"
            f"Передано даних: <code>≈{sent_mb:.2f} МБ</code>\n"
            f"Отримано даних: <code>≈{received_mb:.2f} МБ</code>\n"
            f"Бот працює: <code>{await get_uptime()}</code>\n\n"
            f"🌐 <b>Швидкість інтернету</b>:\n"
            f"Завантаження: <code>{download_speed:.2f} Мбіт/с</code>\n"
            f"Вивантаження: <code>{upload_speed:.2f} Мбіт/с</code>\n"
            f"Пінг: <code>{ping} мс</code>\n\n"
            f"💡 <b>Інформація про сервер</b>:\n"
            f"ОП: <code>{server_info['ram_used'] // MB_FACTOR} / {server_info['ram_total'] // MB_FACTOR} МБ</code>\n"
            f"CPU: <code>{server_info['cpu_load']:.2f}%</code>"
        )

        # Оновлюємо повідомлення з результатами Speedtest
        await bot.edit_message_text(
            chat_id=info_message.chat.id,
            message_id=info_message.message_id,
            text=final_text
        )

    except Exception as e:
        logger.error(f"Помилка в ping_command: {e}")
        await message.answer("Виникла помилка при виконанні команди /ping. Перевірте логи бота.")


# щоб зафіксувати час запуску:
initialize_startup_time()
