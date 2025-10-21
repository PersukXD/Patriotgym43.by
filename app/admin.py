from django.contrib import admin
from .models import PatriotNews, WikiwayImage, HistoricalRegion,Course, ShopItem, UserInventory, UserProfile
from django.utils.html import format_html
from django.contrib import messages


@admin.register(PatriotNews)
class PatriotNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['title', 'text']
    readonly_fields = ['created_at']


@admin.register(WikiwayImage)
class WikiwayImageAdmin(admin.ModelAdmin):
    list_display = [
        'preview_image',
        'title',
        'image_url_short',
        'dimensions',
        'is_parsed',
        'created_at',
        'admin_actions'
    ]
    list_filter = ['is_parsed', 'created_at']
    search_fields = ['title', 'alt_text', 'image_url']
    readonly_fields = ['created_at', 'preview_image_large']
    list_per_page = 25

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'alt_text', 'is_parsed', 'created_at')
        }),
        ('URL изображений', {
            'fields': ('original_src', 'data_src', 'image_url')
        }),
        ('Размеры', {
            'fields': ('width', 'height', 'style_width', 'style_height')
        }),
        ('Превью', {
            'fields': ('preview_image_large',)
        }),
    )

    def preview_image(self, obj):
        """Превью изображения в списке"""
        return format_html(
            '<img src="{}" style="max-width: 50px; max-height: 50px;" onerror="this.style.display=\'none\'" />',
            obj.get_display_url()
        )

    preview_image.short_description = 'Превью'

    def preview_image_large(self, obj):
        """Большое превью в детальном просмотре"""
        return format_html(
            '<img src="{}" style="max-width: 300px; max-height: 300px;" onerror="this.src=\'https://via.placeholder.com/300x200?text=Image+Not+Found\'" />',
            obj.get_display_url()
        )

    preview_image_large.short_description = 'Превью изображения'

    def image_url_short(self, obj):
        """Сокращенный URL для списка"""
        url = obj.image_url
        if len(url) > 50:
            return url[:50] + '...'
        return url

    image_url_short.short_description = 'URL изображения'

    def dimensions(self, obj):
        """Размеры изображения"""
        if obj.width and obj.height:
            return f"{obj.width}×{obj.height}"
        return "—"

    dimensions.short_description = 'Размеры'

    def admin_actions(self, obj):
        """Действия для каждой записи"""
        buttons = [
            format_html(
                '<a href="{}" target="_blank" class="button" style="background-color: #007bff; color: white; padding: 2px 6px; text-decoration: none; border-radius: 3px; margin-right: 5px;">👁️</a>',
                obj.get_display_url()
            ),
            format_html(
                '<a href="../{}/delete/" class="button" style="background-color: #dc3545; color: white; padding: 2px 6px; text-decoration: none; border-radius: 3px;">🗑️</a>',
                obj.id
            )
        ]
        return format_html(' '.join(buttons))

    admin_actions.short_description = 'Действия'

    # Правильное определение actions как списка
    actions = ['delete_selected']

    def get_actions(self, request):
        """Получение доступных действий"""
        actions = super().get_actions(request)
        # Удаляем стандартное delete_selected если нужно
        # del actions['delete_selected']
        return actions

@admin.register(HistoricalRegion)
class HistoricalRegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'period', 'category', 'year', 'is_active']
    list_filter = ['period', 'category', 'is_active']
    search_fields = ['name', 'description', 'stories']
    list_editable = ['is_active']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_range', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['title', 'description', 'additional_info']
    readonly_fields = ['created_at']
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'date_range', 'url', 'image_url')
        }),
        ('Статус', {
            'fields': ('is_completed',)
        }),
        ('Описание', {
            'fields': ('description', 'additional_info', 'organizers')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'category_display',
        'rarity_display',
        'price',
        'image_preview',
        'is_active',
        'created_at'
    ]
    list_filter = ['category', 'rarity', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']
    readonly_fields = ['image_preview_large', 'created_at']
    list_per_page = 20
    actions = ['make_active', 'make_inactive', 'delete_selected_items']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'rarity', 'price', 'is_active')
        }),
        ('Изображения', {
            'fields': ('image', 'preview_image', 'image_preview_large')
        }),
        ('Дополнительно', {
            'fields': ('css_class', 'created_at')
        }),
    )

    def category_display(self, obj):
        return obj.get_category_display()

    category_display.short_description = 'Категория'
    category_display.admin_order_field = 'category'

    def rarity_display(self, obj):
        colors = {
            'common': '#6B7280',
            'rare': '#3B82F6',
            'epic': '#8B5CF6',
            'legendary': '#F59E0B'
        }
        color = colors.get(obj.rarity, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_rarity_display()
        )

    rarity_display.short_description = 'Редкость'
    rarity_display.admin_order_field = 'rarity'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = 'Изображение'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 8px; border: 2px solid #ddd;" />',
                obj.image.url
            )
        return "Изображение не загружено"

    image_preview_large.short_description = 'Предпросмотр изображения'

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} товаров активировано')

    make_active.short_description = "Активировать выбранные товары"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} товаров деактивировано')

    make_inactive.short_description = "Деактивировать выбранные товары"

    def delete_selected_items(self, request, queryset):
        """Кастомное действие для удаления с подтверждением"""
        count = queryset.count()
        for obj in queryset:
            obj.delete()
        self.message_user(request, f'Удалено {count} товаров')

    delete_selected_items.short_description = "Удалить выбранные товары"

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Заменяем стандартное удаление на кастомное
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'purchased_at', 'is_equipped']
    list_filter = ['purchased_at', 'is_equipped', 'item__category']
    search_fields = ['user__username', 'item__name']
    list_per_page = 20
    readonly_fields = ['purchased_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'diamonds', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
