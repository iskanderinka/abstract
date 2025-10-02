import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import tempfile


class AudioProcessor:
    def __init__(self, logger):
        self.logger = logger

    def get_audio_duration(self, file_path):
        """Возвращает длительность аудиофайла в секундах"""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Конвертируем в секунды
        except Exception as e:
            self.logger.error(f"Ошибка при чтении аудиофайла: {e}")
            raise

    def split_audio_by_silence(self, file_path, min_silence_len=2000, silence_thresh=-40):
        """Разбивает аудио на сегменты по паузам"""
        self.logger.info("Начинаем сегментирование аудио по паузам...")

        try:
            # Загружаем аудио
            audio = AudioSegment.from_file(file_path)

            # Разбиваем по паузам
            segments = split_on_silence(
                audio,
                min_silence_len=min_silence_len,  # Минимальная длина паузы в мс
                silence_thresh=silence_thresh,  # Порог тишины в dB
                keep_silence=500  # Оставляем немного тишины в начале/конце сегмента
            )

            self.logger.info(f"Аудио разбито на {len(segments)} сегментов")

            # Сохраняем временные файлы сегментов
            temp_segments = []
            with tempfile.TemporaryDirectory() as temp_dir:
                for i, segment in enumerate(segments):
                    temp_path = os.path.join(temp_dir, f"segment_{i:04d}.wav")
                    segment.export(temp_path, format="wav")
                    temp_segments.append(temp_path)

                # Копируем пути, так как временная директория будет удалена
                segment_paths = temp_segments.copy()

            return segment_paths

        except Exception as e:
            self.logger.error(f"Ошибка при сегментировании аудио: {e}")
            raise

    def convert_audio_format(self, input_path, output_format="wav"):
        """Конвертирует аудио в нужный формат"""
        self.logger.info(f"Конвертируем {input_path} в {output_format}")

        try:
            audio = AudioSegment.from_file(input_path)
            with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as temp_file:
                audio.export(temp_file.name, format=output_format)
                return temp_file.name
        except Exception as e:
            self.logger.error(f"Ошибка конвертации: {e}")
            raise