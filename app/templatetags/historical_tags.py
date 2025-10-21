from django import template

register = template.Library()

@register.filter
def category_color(category):
    colors = {
        'war': '#dc3545',
        'science': '#17a2b8',
        'culture': '#6f42c1',
        'people': '#20c997',
        'mystery': '#fd7e14'
    }
    return colors.get(category, '#007bff')

@register.filter
def category_icon(category):
    icons = {
        'war': '⚔️',
        'science': '🔬',
        'culture': '🎭',
        'people': '👤',
        'mystery': '🔍'
    }
    return icons.get(category, '📍')