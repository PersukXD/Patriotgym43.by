from django.core.management.base import BaseCommand
from app.parsing import run_parsing


class Command(BaseCommand):
    help = 'Парсинг новостей патриотического воспитания'

    def handle(self, *args, **options):
        self.stdout.write('Запуск парсинга...')
        parsed_count, saved_count = run_parsing()
        self.stdout.write(
            self.style.SUCCESS(
                f'Парсинг завершен! Спарсено: {parsed_count}, Сохранено: {saved_count}'
            )
        )