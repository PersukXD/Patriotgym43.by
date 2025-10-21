from django import template

register = template.Library()

@register.filter
def can_delete_post(post, user):
    return post.user_can_delete(user)

@register.filter
def can_delete_comment(comment, user):
    return comment.user_can_delete(user)


@register.filter
def format_audio_filename(filename):
    """Форматирует название аудио файла в читаемый вид"""
    if not filename:
        return 'Аудио файл'

    # Удаляем расширение
    name = filename.replace('.mp3', '').replace('.wav', '').replace('.ogg', '').replace('.m4a', '')

    # Удаляем числовые ID
    import re
    name = re.sub(r'_\d{8,}$', '', name)

    # Заменяем подчеркивания на пробелы
    name = name.replace('_', ' ')

    # Разделяем на части по дефисам
    parts = name.split(' - ')

    if len(parts) >= 2:
        artist = format_name_part(parts[0])
        title = format_name_part(' - '.join(parts[1:]))
        return f'{artist} - {title}'
    else:
        # Пробуем разделить по другим разделителям
        if '_-_' in name:
            parts = name.split('_-_')
            if len(parts) >= 2:
                artist = format_name_part(parts[0])
                title = format_name_part(parts[1])
                return f'{artist} - {title}'

        # Если разделителей нет, форматируем как есть
        return format_name_part(name)


def format_name_part(part):
    """Форматирует часть названия"""
    words = part.split()
    formatted_words = []

    for word in words:
        if len(word) <= 2 and not any(c.isupper() for c in word):
            formatted_words.append(word.lower())
        else:
            formatted_words.append(word.capitalize())

    return ' '.join(formatted_words)