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
from ffmpeg_checker import FFmpegChecker


class LectureTranscriber:
    def __init__(self):
        self.logger = setup_logging()
        self._print_welcome_message()
        self.file_manager = FileManager()
        self.audio_processor = AudioProcessor(self.logger)
        self.transcriber = Transcriber(self.logger, model_size="base")
        self.text_formatter = TextFormatter(line_width=80)

    def _print_welcome_message(self):
        """Выводит приветственное сообщение"""
        print("\n" + "=" * 60)
        print("       ЛЕКЦИЯ -> ТЕКСТ: Транскрибатор лекций")
        print("=" * 60)
        self.logger.info("Инициализация транскрибатора...")

    def process_audio_file(self, audio_path, max_workers=4):
        """Основной метод обработки аудиофайла"""
        try:
            self.logger.info(f"Начинаем обработку файла: {audio_path}")
            print(f"\n🎯 Обрабатываем файл: {os.path.basename(audio_path)}")

            # 1. Валидация файла
            self.file_manager.validate_audio_file(audio_path)
            print("✅ Файл проверен")

            # 2. Анализ длительности
            duration = self.audio_processor.get_audio_duration(audio_path)
            duration_minutes = duration / 60.0
            print(f"⏱️  Длительность аудио: {duration_minutes:.1f} минут")

            # 3. Сегментирование (для длинных файлов)
            if duration > 5 * 60:  # Больше 5 минут
                print("🔊 Сегментируем аудио по паузам...")
                segments = self.audio_processor.split_audio_by_silence(audio_path)
                print(f"📁 Аудио разбито на {len(segments)} сегментов")
            else:
                segments = [audio_path]
                print("📁 Используем файл как один сегмент")

            # 4. Транскрибация
            print("🤖 Загружаем модель распознавания...")
            self.transcriber.load_model()

            print("🎤 Начинаем распознавание речи...")
            results = self.transcriber.transcribe_parallel(segments, max_workers=max_workers)

            # 5. Сборка и форматирование текста
            print("📝 Форматируем текст...")
            final_text = self.text_formatter.assemble_transcript(results)

            if not final_text.strip():
                raise ValueError(
                    "Транскрибация не дала результатов. Возможно, в аудио нет речи или качество записи плохое.")

            # 6. Сохранение результата
            output_path = self.file_manager.generate_output_filename(audio_path)
            self.file_manager.save_text(final_text, output_path)

            # Статистика
            word_count = len(final_text.split())
            char_count = len(final_text)

            print(f"\n✅ Транскрибация завершена!")
            print(f"📄 Результат сохранен в: {output_path}")
            print(f"📊 Статистика: {word_count} слов, {char_count} символов")

            self.logger.info(f"Транскрибация завершена! Результат: {output_path}")
            self.logger.info(f"Статистика: {word_count} слов, {char_count} символов")

            return output_path

        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
            print(f"\n❌ Ошибка: {e}")

            # Для ошибок FFmpeg выводим дополнительные инструкции
            if "ffmpeg" in str(e).lower() or "ffprobe" in str(e).lower():
                print("\n" + "=" * 50)
                print("РЕШЕНИЕ ПРОБЛЕМЫ С FFMPEG:")
                print(FFmpegChecker.get_installation_instructions())
                print("=" * 50)

            raise


def main():
    parser = argparse.ArgumentParser(description='Транскрибатор лекций')
    parser.add_argument('audio_file', help='Путь к аудиофайлу для транскрибации')
    parser.add_argument('--workers', type=int, default=4,
                        help='Количество потоков для обработки (по умолчанию: 4)')
    parser.add_argument('--model', type=str, default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Размер модели Whisper (по умолчанию: base)')

    args = parser.parse_args()

    # Проверяем FFmpeg перед запуском
    print("🔍 Проверяем системные требования...")
    ffmpeg_available, ffmpeg_message = FFmpegChecker.check_ffmpeg()
    if not ffmpeg_available:
        print(f"❌ {ffmpeg_message}")
        print(FFmpegChecker.get_installation_instructions())
        sys.exit(1)

    transcriber = LectureTranscriber()
    transcriber.transcriber.model_size = args.model

    try:
        result_path = transcriber.process_audio_file(args.audio_file, args.workers)
        print(f"\n🎉 Готово! Текст лекции сохранен в файле:")
        print(f"   {result_path}")
    except Exception as e:
        print(f"\n💥 Программа завершена с ошибкой")
        sys.exit(1)


if __name__ == "__main__":
    main()