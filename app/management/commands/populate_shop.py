# В management/commands/populate_shop.py добавьте создание изображений
import os
from django.core.files import File
from django.conf import settings
from django.core.management import BaseCommand

from app.models import ShopItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Создайте простую заглушку программно или используйте существующую
        default_image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'default-shop-item.png')

        items = [
            # Рамки аватарки
            {
                'name': 'Простая серая рамка',
                'description': 'Элегантная простая рамка для вашей аватарки',
                'category': 'avatar_frame',
                'rarity': 'common',
                'price': 1,
                'css_class': 'avatar-frame-common-1'
            },
            {
                'name': 'Синяя рамка',
                'description': 'Стильная синяя рамка с градиентом',
                'category': 'avatar_frame',
                'rarity': 'common',
                'price': 75,
                'css_class': 'avatar-frame-common-2'
            },
            {
                'name': 'Зеленая рамка',
                'description': 'Свежая зеленая рамка',
                'category': 'avatar_frame',
                'rarity': 'common',
                'price': 75,
                'css_class': 'avatar-frame-common-3'
            },
            {
                'name': 'Сияющая синяя рамка',
                'description': 'Рамка с голубым свечением и анимацией',
                'category': 'avatar_frame',
                'rarity': 'rare',
                'price': 150,
                'css_class': 'avatar-frame-rare-1'
            },
            {
                'name': 'Градиентная рамка',
                'description': 'Рамка с красивым градиентом розового и красного',
                'category': 'avatar_frame',
                'rarity': 'rare',
                'price': 200,
                'css_class': 'avatar-frame-rare-2'
            },
            {
                'name': 'Эпическая фиолетовая рамка',
                'description': 'Рамка с фиолетовым пульсирующим свечением',
                'category': 'avatar_frame',
                'rarity': 'epic',
                'price': 300,
                'css_class': 'avatar-frame-epic-1'
            },
            {
                'name': 'Голубая сияющая рамка',
                'description': 'Рамка с голубым свечением и переливами',
                'category': 'avatar_frame',
                'rarity': 'epic',
                'price': 350,
                'css_class': 'avatar-frame-epic-2'
            },
            {
                'name': 'Золотая легендарная рамка',
                'description': 'Роскошная золотая рамка с звездой',
                'category': 'avatar_frame',
                'rarity': 'legendary',
                'price': 1,
                'css_class': 'avatar-frame-legendary-1'
            },
            {
                'name': 'Радужная рамка',
                'description': 'Рамка с переливающимися цветами радуги',
                'category': 'avatar_frame',
                'rarity': 'legendary',
                'price': 600,
                'css_class': 'avatar-frame-legendary-2'
            },
            {
                'name': 'Бриллиантовая рамка',
                'description': 'Изысканная серебряная рамка с бриллиантом',
                'category': 'avatar_frame',
                'rarity': 'legendary',
                'price': 750,
                'css_class': 'avatar-frame-legendary-3'
            },
            # ... добавьте другие категории товаров
        ]

        for item_data in items:
            item, created = ShopItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )

            if created and os.path.exists(default_image_path):
                # Присваиваем заглушку новым товарам
                with open(default_image_path, 'rb') as f:
                    item.image.save('default-shop-item.png', File(f))
                    item.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {item.name}')
                )