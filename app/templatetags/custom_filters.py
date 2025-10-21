from django import template

register = template.Library()


@register.filter
def category_color(category_name):
    """
    Возвращает цвет для категории исторической карты
    """
    if not category_name:
        return '#95a5a6'

    color_map = {
        'войны': '#ff4444',
        'сражения': '#ff6b6b',
        'битвы': '#ff8e8e',
        'революции': '#e74c3c',
        'восстания': '#c0392b',
        'договоры': '#3498db',
        'соглашения': '#2980b9',
        'реформы': '#2ecc71',
        'преобразования': '#27ae60',
        'религия': '#9b59b6',
        'события': '#8e44ad',
        'персоналии': '#f39c12',
        'лидеры': '#e67e22',
        'культура': '#1abc9c',
        'искусство': '#16a085',
        'наука': '#d35400',
        'технологии': '#e67e22',
        'основания': '#34495e',
        'строительства': '#2c3e50',
        'политика': '#2c3e50',
        'по умолчанию': '#95a5a6'
    }

    # Приводим к нижнему регистру для поиска
    category_lower = category_name.lower()

    # Ищем точное совпадение или частичное
    for key, color in color_map.items():
        if key in category_lower:
            return color

    return color_map.get('по умолчанию', '#95a5a6')


@register.filter
def get_item(dictionary, key):
    """
    Получение значения из словаря по ключу в шаблоне
    """
    return dictionary.get(key)


@register.filter
def add_class(field, css_class):
    """
    Добавление CSS класса к полю формы
    """
    return field.as_widget(attrs={"class": css_class})


@register.simple_tag
def get_category_color(category_name):
    """
    Тег для получения цвета категории
    """
    return category_color(category_name)