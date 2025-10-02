# abstract

Приложение для транскрибации длинных аудиозаписей лекций в текст.


## Установка

### 1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd abstract
```

### 2. Установите зависимости:

```bash
pip install -r requirements.txt
```

### 3. Установите FFmpeg (для обработки аудио):
- Ubuntu/Debian:
```bash
sudo apt install ffmpeg
```
- Windows:
  Скачайте с ffmpeg.org
  
- MacOS:
```bash
brew install ffmpeg
```

- Github
```bash
git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
```

## Запуск
```bash
# Базовая транскрибация
python src/main.py путь/к/аудиофайлу.mp3

# С указанием количества потоков
python src/main.py путь/к/аудиофайлу.wav --workers 6
```

## Структура

abstract/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── audio_processor.py
│   ├── transcriber.py
│   ├── text_formatter.py
│   ├── file_manager.py
│   └── logger_config.py
├── output/
├── ver.txt
└── logs/
