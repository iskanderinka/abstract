import whisper
import torch
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm


class Transcriber:
    def __init__(self, logger, model_size="base"):
        self.logger = logger
        self.model_size = model_size
        self.model = None
        self._model_lock = threading.Lock()

    def load_model(self):
        """Загружает модель Whisper (ленивая загрузка)"""
        if self.model is None:
            self.logger.info(f"Загружаем модель Whisper ({self.model_size})...")
            try:
                # Используем GPU если доступен
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.logger.info(f"Используется устройство: {device}")

                self.model = whisper.load_model(self.model_size, device=device)
                self.logger.info("Модель успешно загружена")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки модели: {e}")
                raise

    def transcribe_segment(self, audio_path):
        """Транскрибирует один аудио сегмент"""
        try:
            with self._model_lock:
                if self.model is None:
                    self.load_model()

                result = self.model.transcribe(
                    audio_path,
                    language="ru",  # Явно указываем русский язык
                    fp16=torch.cuda.is_available()  # Используем fp16 на GPU для скорости
                )

            return {
                'text': result['text'].strip(),
                'segments': result.get('segments', [])
            }
        except Exception as e:
            self.logger.error(f"Ошибка транскрибации сегмента {audio_path}: {e}")
            return {'text': '', 'segments': []}

    def transcribe_parallel(self, audio_segments, max_workers=4):
        """Транскрибирует сегменты параллельно"""
        self.logger.info(f"Начинаем параллельную транскрибацию {len(audio_segments)} сегментов...")

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Используем tqdm для прогресс-бара
            futures = list(tqdm(
                executor.map(self.transcribe_segment, audio_segments),
                total=len(audio_segments),
                desc="Транскрибация сегментов"
            ))
            results = list(futures)

        successful = sum(1 for r in results if r['text'])
        self.logger.info(f"Успешно обработано {successful}/{len(audio_segments)} сегментов")

        return results