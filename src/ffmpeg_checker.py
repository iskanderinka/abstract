import shutil
import subprocess
import sys


class FFmpegChecker:
    @staticmethod
    def check_ffmpeg():
        """Проверяет наличие FFmpeg в системе"""
        if shutil.which("ffmpeg") is None:
            return False, "FFmpeg не найден в системе"

        try:
            # Проверяем, что ffmpeg работает
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return False, "FFmpeg установлен, но не работает"

            return True, "FFmpeg доступен"

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return False, f"Ошибка при проверке FFmpeg: {e}"

    @staticmethod
    def get_installation_instructions():
        """Возвращает инструкции по установке для разных ОС"""
        return """
Для установки FFmpeg:

MacOS:
  brew install ffmpeg

Ubuntu/Debian:
  sudo apt update && sudo apt install ffmpeg

Windows:
  Скачайте с https://ffmpeg.org/download.html
  Добавьте в PATH или поместите ffmpeg.exe в папку с программой

Или установите через conda:
  conda install ffmpeg
"""