import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import tempfile
import shutil
from ffmpeg_checker import FFmpegChecker


class AudioProcessor:
    def __init__(self, logger):
        self.logger = logger
        self._check_ffmpeg_availability()

    def _check_ffmpeg_availability(self):
        """Проверяет доступность FFmpeg при инициализации"""
        self.logger.info("Проверяем доступность FFmpeg...")
        is_available, message = FFmpegChecker.check_ffmpeg()

        if not is_available:
            error_msg = f"""
{message}
{FFmpegChecker.get_installation_instructions()}
"""
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        self.logger.info("FFmpeg доступен")

    def get_audio_duration(self, file_path):
        """Возвращает длительность аудиофайла в секундах"""
        self.logger.info(f"Анализируем длительность файла: {file_path}")

        try:
            # Явно указываем использование ffmpeg
            audio = AudioSegment.from_file(file_path, format=None)
            duration_seconds = len(audio) / 1000.0
            self.logger.info(f"Длительность аудио: {duration_seconds:.2f} секунд")
            return duration_seconds

        except Exception as e:
            self.logger.error(f"Ошибка при чтении аудиофайла {file_path}: {e}")

            # Проверяем, существует ли файл
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл не существует: {file_path}")

            # Проверяем права доступа
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"Нет прав на чтение файла: {file_path}")

            raise RuntimeError(f"Не удалось прочитать аудиофайл: {e}")

    def split_audio_by_silence(self, file_path, min_silence_len=2000, silence_thresh=-40):
        """Разбивает аудио на сегменты по паузам"""
        self.logger.info("Начинаем сегментирование аудио по паузам...")

        try:
            # Загружаем аудио
            audio = AudioSegment.from_file(file_path, format=None)

            self.logger.info(f"Аудио загружено, начинаем поиск пауз...")

            # Разбиваем по паузам
            segments = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=500,
                seek_step=100  # Шаг поиска пауз в ms
            )

            self.logger.info(f"Найдено {len(segments)} сегментов по паузам")

            if len(segments) == 0:
                self.logger.warning("Не найдено сегментов по паузам, используем весь файл как один сегмент")
                return [file_path]

            # Сохраняем временные файлы сегментов
            temp_segments = []
            temp_dir = tempfile.mkdtemp()

            for i, segment in enumerate(segments):
                temp_path = os.path.join(temp_dir, f"segment_{i:04d}.wav")
                segment.export(temp_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
                temp_segments.append(temp_path)
                self.logger.debug(f"Создан сегмент {i + 1}/{len(segments)}: {temp_path}")

            self.logger.info(f"Все сегменты сохранены во временную директорию: {temp_dir}")

            return temp_segments

        except Exception as e:
            self.logger.error(f"Ошибка при сегментировании аудио: {e}")
            # В случае ошибки возвращаем исходный файл как один сегмент
            self.logger.info("Возвращаем исходный файл как единый сегмент")
            return [file_path]

    def convert_audio_format(self, input_path, output_format="wav"):
        """Конвертирует аудио в нужный формат"""
        self.logger.info(f"Конвертируем {input_path} в {output_format}")

        try:
            audio = AudioSegment.from_file(input_path, format=None)
            with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as temp_file:
                audio.export(
                    temp_file.name,
                    format=output_format,
                    parameters=["-ac", "1", "-ar", "16000"]  # Моно, 16kHz для лучшего распознавания
                )
                self.logger.info(f"Файл сконвертирован: {temp_file.name}")
                return temp_file.name
        except Exception as e:
            self.logger.error(f"Ошибка конвертации: {e}")
            raise