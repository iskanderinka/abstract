#!/usr/bin/env python3
import os
import sys
import argparse

# Добавляем путь к src для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger_config import setup_logging
from file_manager import FileManager
from audio_processor import AudioProcessor
from transcriber import Transcriber
from text_formatter import TextFormatter


class LectureTranscriber:
    def __init__(self):
        self.logger = setup_logging()
        self.file_manager = FileManager()
        self.audio_processor = AudioProcessor(self.logger)
        self.transcriber = Transcriber(self.logger, model_size="base")
        self.text_formatter = TextFormatter(line_width=80)

    def process_audio_file(self, audio_path, max_workers=4):
        """Основной метод обработки аудиофайла"""
        try:
            self.logger.info(f"Начинаем обработку файла: {audio_path}")

            # 1. Валидация файла
            self.file_manager.validate_audio_file(audio_path)

            # 2. Анализ длительности
            duration = self.audio_processor.get_audio_duration(audio_path)
            self.logger.info(f"Длительность аудио: {duration / 60:.2f} минут")

            # 3. Сегментирование (для длинных файлов)
            if duration > 10 * 60:  # Больше 10 минут
                self.logger.info("Файл длинный, применяем сегментирование...")
                segments = self.audio_processor.split_audio_by_silence(audio_path)
            else:
                segments = [audio_path]

            # 4. Транскрибация
            self.transcriber.load_model()
            results = self.transcriber.transcribe_parallel(segments, max_workers=max_workers)

            # 5. Сборка и форматирование текста
            final_text = self.text_formatter.assemble_transcript(results)

            if not final_text.strip():
                raise ValueError("Транскрибация не дала результатов")

            # 6. Сохранение результата
            output_path = self.file_manager.generate_output_filename(audio_path)
            self.file_manager.save_text(final_text, output_path)

            self.logger.info(f"Транскрибация завершена! Результат сохранен в: {output_path}")

            # Статистика
            word_count = len(final_text.split())
            self.logger.info(f"Статистика: {word_count} слов, {len(final_text)} символов")

            return output_path

        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description='Транскрибатор лекций')
    parser.add_argument('audio_file', help='Путь к аудиофайлу для транскрибации')
    parser.add_argument('--workers', type=int, default=4,
                        help='Количество потоков для обработки (по умолчанию: 4)')

    args = parser.parse_args()

    transcriber = LectureTranscriber()

    try:
        result_path = transcriber.process_audio_file(args.audio_file, args.workers)
        print(f"\n✅ Транскрибация завершена! Файл сохранен: {result_path}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()