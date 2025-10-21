from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files import File
import os
from urllib.parse import urlparse

import requests
from io import BytesIO


class PatriotNews(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    date = models.DateField(verbose_name="Дата")
    main_image = models.URLField(max_length=500, blank=True, null=True, verbose_name="Главное изображение")
    text = models.TextField(verbose_name="Текст")
    additional_images = models.JSONField(default=list, blank=True, verbose_name="Дополнительные изображения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Новость патриотического воспитания"
        verbose_name_plural = "Новости патриотического воспитания"
        ordering = ['-date']

    def __str__(self):
        return self.title

    def get_detail_url(self):
        """Возвращает URL для детальной страницы (пока используем главное изображение)"""
        return self.main_image if self.main_image else "#"

    def has_additional_images(self):
        """Проверяет есть ли дополнительные изображения"""
        return len(self.additional_images) > 0


def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'


class ShopItem(models.Model):
    CATEGORY_CHOICES = [
        ('avatar_frame', 'Рамка аватарки'),
        ('profile_background', 'Фон профиля'),
        ('badge', 'Значок'),
        ('title', 'Особый титул'),
        ('animation', 'Анимация'),
    ]

    RARITY_CHOICES = [
        ('common', 'Обычный'),
        ('rare', 'Редкий'),
        ('epic', 'Эпический'),
        ('legendary', 'Легендарный'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категория")
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, verbose_name="Редкость")
    price = models.IntegerField(verbose_name="Цена в алмазах")
    image = models.ImageField(upload_to='shop/items/', verbose_name="Изображение товара", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL изображения")
    preview_image = models.ImageField(upload_to='shop/previews/', blank=True, null=True, verbose_name="Превью")
    css_class = models.CharField(max_length=100, blank=True, verbose_name="CSS класс для стилизации")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Товар магазина"
        verbose_name_plural = "Товары магазина"
        ordering = ['category', 'price']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - {self.price} алмазов"

    def get_rarity_color(self):
        colors = {
            'common': '#6B7280',  # серый
            'rare': '#3B82F6',  # синий
            'epic': '#8B5CF6',  # фиолетовый
            'legendary': '#F59E0B',  # золотой
        }
        return colors.get(self.rarity, '#6B7280')

    def get_image_url(self):
        """Безопасное получение URL изображения - приоритет у URL, потом у файла"""
        if self.image_url:
            return self.image_url
        elif self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-shop-item.png'

    def get_preview_url(self):
        """Безопасное получение URL превью"""
        if self.preview_image and hasattr(self.preview_image, 'url'):
            return self.preview_image.url
        return self.get_image_url()

    def get_rarity_display_with_emoji(self):
        """Отображение редкости с эмодзи (без рекурсии)"""
        rarity_emojis = {
            'common': '⚪',
            'rare': '🔵',
            'epic': '🟣',
            'legendary': '🟡'
        }
        emoji = rarity_emojis.get(self.rarity, '⚪')

        # Получаем человеко-читаемое название из RARITY_CHOICES
        rarity_dict = dict(self.RARITY_CHOICES)
        rarity_name = rarity_dict.get(self.rarity, self.rarity)

        return f"{emoji} {rarity_name}"


class UserInventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_equipped = models.BooleanField(default=False, verbose_name="Надето")

    class Meta:
        verbose_name = "Инвентарь пользователя"
        verbose_name_plural = "Инвентари пользователей"
        unique_together = ['user', 'item']

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"


class AvatarFrame(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='avatar_frames/')
    price = models.IntegerField(default=0)
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Обычная'),
        ('rare', 'Редкая'),
        ('epic', 'Эпическая'),
        ('legendary', 'Легендарная'),
    ], default='common')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Badge(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='badges/')
    description = models.TextField()
    display_on_avatar = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    status = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    diamonds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Убраны проблемные поля - используем только ShopItem
    active_avatar_frame = models.ForeignKey(ShopItem, on_delete=models.SET_NULL,
                                            null=True, blank=True,
                                            related_name='active_avatar_frames',
                                            verbose_name="Активная рамка аватарки",
                                            limit_choices_to={'category': 'avatar_frame'})
    active_profile_background = models.ForeignKey(ShopItem, on_delete=models.SET_NULL,
                                                  null=True, blank=True,
                                                  related_name='active_backgrounds',
                                                  verbose_name="Активный фон профиля",
                                                  limit_choices_to={'category': 'profile_background'})
    active_badge = models.ForeignKey(ShopItem, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='active_badges',
                                     verbose_name="Активный значок",
                                     limit_choices_to={'category': 'badge'})

    def __str__(self):
        return f"Профиль {self.user.username}"

    def get_friends_count(self):
        return self.friends.count()

    def get_posts_count(self):
        return self.user.post_set.count()

    def add_diamonds(self, amount):
        """Добавить алмазы пользователю"""
        self.diamonds += amount
        self.save()
        return self.diamonds

    def spend_diamonds(self, amount):
        """Потратить алмазы (если достаточно)"""
        if self.diamonds >= amount:
            self.diamonds -= amount
            self.save()
            return True
        return False

    def get_equipped_items(self):
        """Возвращает список надетых предметов из инвентаря"""
        equipped_items = UserInventory.objects.filter(
            user=self.user,
            is_equipped=True
        ).select_related('item')

        return equipped_items

    def get_equipped_avatar_frame(self):
        """Получить надетую рамку аватара"""
        try:
            return UserInventory.objects.get(
                user=self.user,
                item__category='avatar_frame',
                is_equipped=True
            )
        except UserInventory.DoesNotExist:
            return None


class Friendship(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, related_name='friendship_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.user.username} -> {self.to_user.user.username}"


class Post(models.Model):
    POST_TYPES = [
        ('text', 'Текст'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('audio', 'Аудио'),
    ]

    author = models.ForeignKey(User, related_name='post_set', on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Текст поста")
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    media_file = models.FileField(upload_to='posts/media/', blank=True, null=True)
    audio_cover = models.ImageField(upload_to='posts/audio_covers/', blank=True, null=True,
                                    verbose_name="Обложка аудио")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Пост от {self.author.username}"

    def user_can_delete(self, user):
        """Проверяет, может ли пользователь удалить пост"""
        return user.is_authenticated and (user == self.author or user.is_staff)


class UserQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quests')
    quest_type = models.CharField(max_length=100, verbose_name="Тип задания")
    difficulty = models.CharField(max_length=20, verbose_name="Сложность")
    completed = models.BooleanField(default=False, verbose_name="Выполнено")
    diamonds_earned = models.IntegerField(default=0, verbose_name="Заработано алмазов")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата выполнения")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.quest_type} ({self.difficulty})"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def user_can_delete(self, user):
        """Проверяет, может ли пользователь удалить комментарий"""
        return user.is_authenticated and (user == self.user or user == self.post.author or user.is_staff)


class WikiwayImage(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    alt_text = models.TextField(blank=True, verbose_name="Alt текст")
    original_src = models.URLField(max_length=1000, verbose_name="Original SRC")
    data_src = models.URLField(max_length=1000, blank=True, verbose_name="Data SRC")
    image_url = models.URLField(max_length=1000, verbose_name="URL изображения")
    width = models.IntegerField(blank=True, null=True, verbose_name="Ширина")
    height = models.IntegerField(blank=True, null=True, verbose_name="Высота")
    style_width = models.CharField(max_length=50, blank=True, verbose_name="Ширина в стиле")
    style_height = models.CharField(max_length=50, blank=True, verbose_name="Высота в стиле")
    is_parsed = models.BooleanField(default=False, verbose_name="Парсинг завершен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Изображение Wikiway"
        verbose_name_plural = "Изображения Wikiway"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_final_image_url(self):
        """Получение конечного URL изображения (предпочтительно data-src)"""
        return self.data_src if self.data_src else self.original_src

    def get_display_url(self):
        """URL для отображения в галерее"""
        image_url = self.get_final_image_url()
        # Убеждаемся что URL абсолютный
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        elif image_url.startswith('/'):
            image_url = 'https://wikiway.com' + image_url
        return image_url

    def get_filename(self):
        """Получение имени файла из URL"""
        url = self.get_display_url()
        parsed_url = urlparse(url)
        return parsed_url.path.split('/')[-1] if '/' in parsed_url.path else 'image'


class HistoricalRegion(models.Model):
    PERIOD_CHOICES = [
        ('ancient', 'Древность (до X века)'),
        ('middle_ages', 'Средневековье (X-XV века)'),
        ('grand_duchy', 'Великое Княжество Литовское (XIII-XVI века)'),
        ('polish_lithuanian', 'Речь Посполитая (XVI-XVIII века)'),
        ('russian_empire', 'В составе Российской империи (XVIII-XX века)'),
        ('soviet', 'Советский период (1917-1991)'),
        ('modern', 'Современная Беларусь (с 1991)'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название региона/города")
    description = models.TextField(verbose_name="Описание")
    stories = models.TextField(verbose_name="Интересные истории", help_text="Разделяйте истории точкой с запятой")
    coordinates = models.JSONField(verbose_name="Координаты полигона",
                                   help_text="JSON с координатами для отрисовки на карте")
    center_lat = models.FloatField(verbose_name="Центральная широта")
    center_lng = models.FloatField(verbose_name="Центральная долгота")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name="Исторический период")
    year = models.IntegerField(verbose_name="Год события", blank=True, null=True)
    category = models.CharField(max_length=100, choices=[
        ('war', 'Военные подвиги'),
        ('science', 'Наука и изобретения'),
        ('culture', 'Культура и искусство'),
        ('people', 'Выдающиеся личности'),
        ('mystery', 'Загадки и тайны'),
    ], verbose_name="Категория")
    image = models.ImageField(upload_to='historical_regions/', blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_historical_regions'
        verbose_name = "Исторический регион"
        verbose_name_plural = "Исторические регионы"
        ordering = ['period', 'year']

    def __str__(self):
        return f"{self.name} ({self.get_period_display()})"

    def get_stories_list(self):
        """Возвращает список историй"""
        return [story.strip() for story in self.stories.split(';') if story.strip()]

    def get_category_icon(self):
        """Возвращает иконку для категории"""
        icons = {
            'war': '⚔️',
            'science': '🔬',
            'culture': '🎭',
            'people': '👤',
            'mystery': '🔍',
        }
        return icons.get(self.category, '📍')



class Course(models.Model):
    title = models.CharField(max_length=500, verbose_name="Название курса")
    date_range = models.CharField(max_length=100, verbose_name="Период проведения")
    image_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name="URL изображения")
    is_completed = models.BooleanField(default=False, verbose_name="Мероприятие завершено")
    description = models.TextField(blank=True, verbose_name="Описание")
    additional_info = models.TextField(blank=True, verbose_name="Дополнительная информация")
    organizers = models.TextField(blank=True, verbose_name="Организаторы")
    url = models.URLField(max_length=1000, verbose_name="URL курса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'app_patriot_courses'
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# Исправленные сигналы
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()




# Добавьте поле в UserProfile для активных украшений
# Добавьте это в класс UserProfile (если еще нет):
