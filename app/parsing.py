
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import json


def parse_patriot_news():
    url = "https://krivonosy.starye-dorogi.by/воспитательная-работа/патриот-by"

    try:
        # Отправляем запрос к странице
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Парсим HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Находим все элементы с классом spoiler item entry
        news_items = soup.find_all('div', class_='spoiler item entry')

        parsed_news = []

        for item in news_items:
            try:
                # 1. Парсим изображение из preview
                preview_div = item.find('div', class_='preview col-xs-12 col-sm-2')
                if preview_div:
                    img_tag = preview_div.find('img', class_='img-responsive')
                    main_image = img_tag.get('src') if img_tag else None

                    if main_image and not main_image.startswith('http'):
                        main_image = urljoin(url, main_image)
                else:
                    main_image = None

                # 2. Парсим заголовок и дату из content
                content_div = item.find('div', class_='content')
                if content_div:
                    # Заголовок
                    title_tag = content_div.find('h3')
                    title = title_tag.get_text(strip=True) if title_tag else "Без названия"

                    # Дата
                    date_span = content_div.find('span', class_='date')
                    date_str = date_span.get_text(strip=True) if date_span else None

                    # Преобразуем дату
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%d.%m.%Y').date()
                        except ValueError:
                            date_obj = datetime.now().date()
                    else:
                        date_obj = datetime.now().date()
                else:
                    title = "Без названия"
                    date_obj = datetime.now().date()

                # 3. Парсим текст и дополнительные изображения из spoiler_content
                spoiler_content = item.find('div', class_='spoiler_content')
                text_content = ""
                additional_images = []

                if spoiler_content:
                    # Находим все параграфы и изображения
                    elements = spoiler_content.find_all(['p', 'img'])

                    for element in elements:
                        if element.name == 'p':
                            # Текст из параграфа
                            paragraph_text = element.get_text(strip=True)
                            if paragraph_text:
                                if text_content:
                                    text_content += " " + paragraph_text
                                else:
                                    text_content = paragraph_text
                        elif element.name == 'img':
                            # Дополнительные изображения
                            img_src = element.get('src')
                            if img_src:
                                if not img_src.startswith('http'):
                                    img_src = urljoin(url, img_src)
                                additional_images.append(img_src)

                # Создаем объект новости
                news_data = {
                    'title': title,
                    'date': date_obj,
                    'main_image': main_image,
                    'text': text_content,
                    'additional_images': additional_images
                }

                parsed_news.append(news_data)
                print(f"Успешно спарсено: {title}")

            except Exception as e:
                print(f"Ошибка при парсинге элемента: {e}")
                continue

        return parsed_news

    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return []
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return []


def save_to_database(parsed_data):
    from .models import PatriotNews

    saved_count = 0
    for news_item in parsed_data:
        try:
            # Проверяем, существует ли уже такая новость (по заголовку и дате)
            existing_news = PatriotNews.objects.filter(
                title=news_item['title'],
                date=news_item['date']
            ).exists()

            if not existing_news:
                PatriotNews.objects.create(
                    title=news_item['title'],
                    date=news_item['date'],
                    main_image=news_item['main_image'],
                    text=news_item['text'],
                    additional_images=news_item['additional_images']
                )
                saved_count += 1
                print(f"Сохранено в БД: {news_item['title']}")
            else:
                print(f"Новость уже существует: {news_item['title']}")

        except Exception as e:
            print(f"Ошибка при сохранении в БД: {e}")

    return saved_count


def run_parsing():
    print("Начало парсинга...")
    parsed_data = parse_patriot_news()
    print(f"Спарсено {len(parsed_data)} новостей")

    if parsed_data:
        saved_count = save_to_database(parsed_data)
        print(f"Сохранено {saved_count} новых записей в БД")
    else:
        print("Не удалось спарсить данные")

    return len(parsed_data), saved_count