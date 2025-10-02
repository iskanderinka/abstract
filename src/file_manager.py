import os
import re
from pathlib import Path


class FileManager:
    def __init__(self):
        self.output_dir = "output"
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Создает папку для результатов если её нет"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def validate_audio_file(self, file_path):
        """Проверяет существование и доступность аудиофайла"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Указанный путь не является файлом: {file_path}")

        return True

    def generate_output_filename(self, input_path):
        """Генерирует имя для выходного файла на основе входного"""
        input_name = Path(input_path).stem
        # Очищаем имя от специальных символов
        clean_name = re.sub(r'[^\w\s-]', '', input_name)
        output_path = os.path.join(self.output_dir, f"{clean_name}_transcript.txt")

        # Если файл существует, добавляем номер
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(self.output_dir, f"{clean_name}_transcript_{counter}.txt")
            counter += 1

        return output_path

    def save_text(self, text, output_path):
        """Сохраняет текст в файл"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return output_path