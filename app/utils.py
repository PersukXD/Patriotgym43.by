# app/utils.py - создайте новый файл
import os
import mutagen
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def extract_audio_cover(audio_file):
    """
    Извлекает обложку из аудио файла (MP3)
    Возвращает ContentFile с изображением или None
    """
    try:
        audio = mutagen.File(audio_file)
        if audio is None:
            return None

        # Ищем обложку в тегах
        for tag in audio.tags.values():
            if hasattr(tag, 'data') and tag.data:
                # Проверяем, является ли данные изображением
                if hasattr(tag, 'mime') and tag.mime and 'image' in tag.mime:
                    image_data = tag.data
                    break
                else:
                    # Пробуем определить тип изображения по первым байтам
                    if tag.data.startswith(b'\xff\xd8'):
                        # JPEG
                        image_data = tag.data
                        break
                    elif tag.data.startswith(b'\x89PNG'):
                        # PNG
                        image_data = tag.data
                        break
            elif hasattr(tag, 'pictype') and hasattr(tag, 'data'):
                # Для ID3v2.2
                image_data = tag.data
                break
        else:
            return None

        # Создаем изображение из данных
        image = Image.open(BytesIO(image_data))

        # Конвертируем в JPEG если нужно и ресайзим
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Ресайзим до разумных размеров
        max_size = (500, 500)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Сохраняем в буфер
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85)

        # Создаем ContentFile
        file_name = os.path.splitext(audio_file.name)[0] + '_cover.jpg'
        return ContentFile(buffer.getvalue(), name=file_name)

    except Exception as e:
        print(f"Ошибка при извлечении обложки: {e}")
        return None