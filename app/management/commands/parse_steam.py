# app/management/commands/parse_steam.py
from django.core.management.base import BaseCommand
from app.steam_parser import run_steam_parsing


class Command(BaseCommand):
    help = 'Парсинг рамок аватаров из Steam Points Shop'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Запуск парсера Steam Points Shop...")

        parsed_count, saved_count = run_steam_parsing()

        if saved_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'🎉 Успешно! Сохранено: {saved_count} товаров')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Не сохранено новых товаров')
            )