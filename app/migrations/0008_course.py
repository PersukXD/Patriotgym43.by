# app/migrations/0008_course_only.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_post_audio_cover'),  # Замените на актуальную предыдущую миграцию
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='Название курса')),
                ('date_range', models.CharField(max_length=100, verbose_name='Период проведения')),
                ('image_url', models.URLField(blank=True, max_length=1000, null=True, verbose_name='URL изображения')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Мероприятие завершено')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('additional_info', models.TextField(blank=True, verbose_name='Дополнительная информация')),
                ('organizers', models.TextField(blank=True, verbose_name='Организаторы')),
                ('url', models.URLField(max_length=1000, verbose_name='URL курса')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'db_table': 'app_patriot_courses',
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
                'ordering': ['-created_at'],
            },
        ),
    ]