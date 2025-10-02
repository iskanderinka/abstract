import logging
import os
from datetime import datetime


def setup_logging():
    """Настройка системы логирования"""

    # Создаем папку для логов если её нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Форматирование
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Настройка базового логгера
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(f"{log_dir}/transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()  # Вывод в консоль
        ]
    )

    return logging.getLogger(__name__)