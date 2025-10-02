import textwrap
import re


class TextFormatter:
    def __init__(self, line_width=80):
        self.line_width = line_width

    def assemble_transcript(self, segment_results, min_pause_for_paragraph=3.0):
        """Собирает транскрипт из результатов сегментов с форматированием"""
        if not segment_results:
            return ""

        paragraphs = []
        current_paragraph = []

        for i, result in enumerate(segment_results):
            if not result['text']:
                continue

            # Добавляем текст текущего сегмента
            current_paragraph.append(result['text'])

            # Проверяем паузу до следующего сегмента
            if i < len(segment_results) - 1:
                current_segments = result.get('segments', [])
                next_segments = segment_results[i + 1].get('segments', [])

                if current_segments and next_segments:
                    end_current = current_segments[-1]['end']
                    start_next = next_segments[0]['start']
                    pause_duration = start_next - end_current

                    # Если пауза большая - начинаем новый абзац
                    if pause_duration >= min_pause_for_paragraph:
                        if current_paragraph:
                            paragraphs.append(" ".join(current_paragraph))
                            current_paragraph = []

        # Добавляем последний абзац
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        return self._format_paragraphs(paragraphs)

    def _format_paragraphs(self, paragraphs):
        """Форматирует абзацы с переносом строк"""
        formatted_text = []

        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # Форматируем абзац с ограничением длины строки
                wrapped_paragraph = textwrap.fill(
                    paragraph,
                    width=self.line_width,
                    break_long_words=False,
                    break_on_hyphens=False
                )
                formatted_text.append(wrapped_paragraph)

                # Добавляем пустую строку между абзацами (кроме последнего)
                if i < len(paragraphs) - 1:
                    formatted_text.append("")

        return "\n".join(formatted_text)

    def add_timestamps(self, text, segment_results):
        """Добавляет временные метки (опционально)"""
        # Здесь можно добавить функционал временных меток
        # если потребуется
        return text