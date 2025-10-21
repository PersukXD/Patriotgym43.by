# management/commands/parse_courses.py
from django.core.management.base import BaseCommand
from app.services_2 import CourseParser, save_courses_to_db
import time


class Command(BaseCommand):
    help = 'Parse courses from patriot.rcek.by'

    def add_arguments(self, parser):
        parser.add_argument(
            '--headless',
            action='store_true',
            default=True,
            help='Run browser in headless mode (default: True)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Limit number of courses to parse (default: 20)',
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=2,
            help='Number of pages to load (default: 2)',
        )
        parser.add_argument(
            '--skip-save',
            action='store_true',
            help='Skip saving to database (only parse)',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting courses parsing...')

        headless = options['headless']
        limit = options['limit']
        pages = options['pages']
        skip_save = options['skip_save']

        start_time = time.time()

        try:
            with CourseParser(headless=headless) as parser:
                # Парсим курсы с поддержкой пагинации
                courses_data = parser.parse_courses(limit=limit, max_pages=pages)

            elapsed_time = time.time() - start_time

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully parsed {len(courses_data)} courses from {pages} pages in {elapsed_time:.2f} seconds'
                )
            )

            # Сохраняем в базу данных если не пропущено
            if not skip_save and courses_data:
                saved_count = save_courses_to_db(courses_data)
                self.stdout.write(
                    self.style.SUCCESS(f'💾 Successfully saved {saved_count} courses to database')
                )
            elif skip_save:
                self.stdout.write('⏭️ Skipped saving to database')
            else:
                self.stdout.write(self.style.WARNING('📭 No courses to save'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during parsing: {str(e)}')
            )
            import traceback
            self.stdout.write(self.style.ERROR(f'🔍 Details: {traceback.format_exc()}'))