# app/steam_parser.py
import os
import sys
import django
from django.core.files import File
from io import BytesIO
import requests
from urllib.parse import urlparse
import time
import random

# Добавляем путь к проекту Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Patriot.settings')
django.setup()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from app.models import ShopItem


class SteamPointsShopParser:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.base_url = "https://store.steampowered.com/points/shop/c/home/cluster/10"

    def setup_driver(self):
        """Настройка Chrome драйвера"""
        print("🔧 Настройка Chrome драйвера...")

        try:
            chrome_options = Options()

            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")

            if self.headless:
                chrome_options.add_argument("--headless")

            print("📥 Установка ChromeDriver...")
            service = Service(ChromeDriverManager().install())

            print("🚀 Запуск Chrome...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)

            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("✅ Chrome драйвер успешно настроен")
            return True

        except Exception as e:
            print(f"❌ Ошибка настройки Chrome драйвера: {e}")
            return False

    def close_driver(self):
        """Закрытие драйвера"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔴 Chrome драйвер закрыт")
            except:
                pass

    def safe_get_page(self, url):
        """Безопасная загрузка страницы"""
        try:
            print(f"🌐 Загрузка страницы: {url}")

            self.driver.get(url)
            time.sleep(8)

            if "Steam" in self.driver.title or "points" in self.driver.current_url:
                print("✅ Страница успешно загружена")
                return True
            else:
                print("⚠️ Страница загрузилась, но не похожа на Steam")
                return True

        except TimeoutException:
            print("⚠️ Таймаут загрузки, продолжаем...")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки страницы: {e}")
            return False

    def scroll_page(self):
        """Прокрутка страницы с обработкой динамического контента"""
        print("📜 Прокрутка страницы...")

        try:
            scroll_pause_time = 2
            max_scrolls = 10
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0

            while scroll_count < max_scrolls:
                print(f"🔄 Прокрутка {scroll_count + 1}/{max_scrolls}...")

                # Прокручиваем до конца
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)

                # Ждем немного для загрузки контента
                time.sleep(1)

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("📏 Достигнут конец страницы")
                    break

                last_height = new_height
                scroll_count += 1

            print("✅ Прокрутка завершена")

        except Exception as e:
            print(f"⚠️ Ошибка при прокрутке: {e}")

    def parse_steam_items(self):
        """Основной метод парсинга"""
        print("🚀 Начало парсинга Steam Points Shop...")

        if not self.setup_driver():
            return []

        try:
            if not self.safe_get_page(self.base_url):
                return []

            self.scroll_page()

            # Сохраняем HTML для отладки
            page_html = self.driver.page_source
            with open("steam_page_debug.html", "w", encoding="utf-8") as f:
                f.write(page_html)
            print("📄 HTML страницы сохранен: steam_page_debug.html")

            # Ищем карточки с помощью стабильного метода
            frames_data = self.find_avatar_frames_stable()

            if not frames_data:
                print("❌ Не найдено карточек с рамками аватаров")
                return []

            print(f"📦 Найдено карточек с рамками: {len(frames_data)}")

            parsed_items = []

            for i, frame_data in enumerate(frames_data):
                try:
                    print(f"\n🔄 Обработка карточки {i + 1}/{len(frames_data)}")
                    print(f"🏷️ Название: {frame_data['name']}")
                    print(f"🖼️ Изображение: {frame_data['image_url'][:80]}...")

                    item_data = {
                        'name': frame_data['name'],
                        'description': f"Рамка аватара из Steam Points Shop. {frame_data['name']}",
                        'category': 'avatar_frame',
                        'rarity': 'common',
                        'price': 300,
                        'image_url': frame_data['image_url'],
                    }

                    parsed_items.append(item_data)
                    print(f"✅ Успешно обработана: {frame_data['name']}")

                except Exception as e:
                    print(f"❌ Ошибка при обработке карточки {i + 1}: {e}")
                    continue

            return parsed_items

        except Exception as e:
            print(f"❌ Критическая ошибка при парсинге: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            self.close_driver()

    def find_avatar_frames_stable(self):
        """Стабильный поиск рамок аватаров с обработкой stale elements"""
        frames_data = []

        print("🔍 Поиск карточек стабильным методом...")

        try:
            # Получаем HTML страницы и парсим с BeautifulSoup
            page_html = self.driver.page_source
            soup = BeautifulSoup(page_html, 'html.parser')

            # Ищем все карточки через BeautifulSoup (более стабильно)
            frames_data = self.parse_cards_with_bs4(soup)

            # Если не нашли через BS4, пробуем Selenium с перезапросом элементов
            if not frames_data:
                print("🔍 Пробуем поиск через Selenium с перезапросом...")
                frames_data = self.parse_cards_with_selenium_retry()

        except Exception as e:
            print(f"❌ Ошибка при поиске карточек: {e}")

        return frames_data

    def parse_cards_with_bs4(self, soup):
        """Парсинг карточек через BeautifulSoup (без stale elements)"""
        frames_data = []

        # Ищем все карточки по классу
        cards = soup.find_all('div', class_='padding-top-large')
        print(f"🔍 Найдено карточек через BS4: {len(cards)}")

        for card in cards:
            try:
                # Ищем тип товара
                type_element = card.find(class_='_2FQCUXF5fJTFVBLk8XgRUd')
                if not type_element:
                    continue

                item_type = type_element.get_text(strip=True)

                # Проверяем, что это рамка аватара
                if "Рамка аватара" not in item_type:
                    continue

                # Ищем название
                name_element = card.find(class_='EccZY8FXMaK1CgBOE2ztA')
                if not name_element:
                    continue

                item_name = name_element.get_text(strip=True)
                if not item_name:
                    continue

                # Ищем изображение
                img_element = card.find('img', class_='_2MPpwm3uMppV0DPtkN4Pp_')
                if not img_element:
                    continue

                image_url = (img_element.get('src') or
                             img_element.get('data-src') or
                             img_element.get('data-lazy-src') or "")

                if not image_url:
                    continue

                # Преобразуем URL к правильному формату
                image_url = self.normalize_image_url(image_url)

                # Очищаем название
                item_name = " ".join(item_name.split())

                frames_data.append({
                    'name': item_name,
                    'image_url': image_url,
                    'type': item_type
                })

                print(f"✅ Найдена рамка через BS4: {item_name}")

            except Exception as e:
                print(f"⚠️ Ошибка при обработке карточки BS4: {e}")
                continue

        return frames_data

    def parse_cards_with_selenium_retry(self):
        """Парсинг карточек через Selenium с перезапросом элементов"""
        frames_data = []

        try:
            # Постоянно перезапрашиваем элементы чтобы избежать stale reference
            cards = self.driver.find_elements(By.CSS_SELECTOR, "div.padding-top-large")
            print(f"🔍 Найдено карточек через Selenium: {len(cards)}")

            for i in range(len(cards)):
                try:
                    # Каждый раз перезапрашиваем элементы
                    current_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.padding-top-large")
                    if i >= len(current_cards):
                        break

                    card = current_cards[i]

                    # Быстро получаем данные без лишних взаимодействий
                    card_data = self.get_card_data_quick(card, i)
                    if card_data:
                        frames_data.append(card_data)

                except StaleElementReferenceException:
                    print(f"🔄 Stale element для карточки {i + 1}, пропускаем...")
                    continue
                except Exception as e:
                    print(f"⚠️ Ошибка при обработке карточки {i + 1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Ошибка при Selenium парсинге: {e}")

        return frames_data

    def get_card_data_quick(self, card, index):
        """Быстрое получение данных карточки с минимумом взаимодействий"""
        try:
            # Получаем HTML карточки и парсим через BS4
            card_html = card.get_attribute('outerHTML')
            card_soup = BeautifulSoup(card_html, 'html.parser')

            # Ищем тип товара
            type_element = card_soup.find(class_='_2FQCUXF5fJTFVBLk8XgRUd')
            if not type_element:
                return None

            item_type = type_element.get_text(strip=True)

            # Проверяем, что это рамка аватара
            if "Рамка аватара" not in item_type:
                return None

            # Ищем название
            name_element = card_soup.find(class_='EccZY8FXMaK1CgBOE2ztA')
            if not name_element:
                return None

            item_name = name_element.get_text(strip=True)
            if not item_name:
                return None

            # Ищем изображение
            img_element = card_soup.find('img', class_='_2MPpwm3uMppV0DPtkN4Pp_')
            if not img_element:
                return None

            image_url = (img_element.get('src') or
                         img_element.get('data-src') or
                         img_element.get('data-lazy-src') or "")

            if not image_url:
                return None

            # Преобразуем URL
            image_url = self.normalize_image_url(image_url)

            # Очищаем название
            item_name = " ".join(item_name.split())

            print(f"✅ Найдена рамка через Selenium: {item_name}")

            return {
                'name': item_name,
                'image_url': image_url,
                'type': item_type
            }

        except Exception as e:
            print(f"⚠️ Ошибка при быстром парсинге карточки {index + 1}: {e}")
            return None

    def normalize_image_url(self, image_url):
        """Преобразование URL изображения к правильному формату"""
        if not image_url:
            return image_url

        # Если URL относительный, делаем абсолютным
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        elif image_url.startswith('/'):
            image_url = 'https://shared.fastly.steamstatic.com' + image_url

        return image_url

    def save_to_database(self, item_data):
        """Сохранение товара в базу данных"""
        try:
            # Проверяем, существует ли уже такой товар
            existing_item = ShopItem.objects.filter(
                name=item_data['name'],
                category='avatar_frame'
            ).first()

            if existing_item:
                print(f"⚠️ Товар уже существует: {item_data['name']}")
                return False

            # Создаем запись товара
            shop_item = ShopItem(
                name=item_data['name'],
                description=item_data['description'],
                category=item_data['category'],
                rarity=item_data['rarity'],
                price=item_data['price'],
                image_url=item_data['image_url'],
                is_active=True
            )

            # Сохраняем без файла изображения
            shop_item.save()

            print(f"✅ Товар сохранен в базу: {item_data['name']}")
            return True

        except Exception as e:
            print(f"❌ Ошибка при сохранении в базу: {e}")
            return False


def run_steam_parsing():
    """Функция для запуска парсинга через консоль"""
    print("=" * 60)
    print("🎮 ПАРСЕР STEAM POINTS SHOP")
    print("=" * 60)

    parser = SteamPointsShopParser(headless=False)

    try:
        items_data = parser.parse_steam_items()

        if not items_data:
            print("\n❌ Не найдено подходящих товаров для сохранения")
            return 0, 0

        saved_count = 0
        print(f"\n💾 Сохранение {len(items_data)} товаров в базу...")

        for i, item_data in enumerate(items_data, 1):
            print(f"\n📥 [{i}/{len(items_data)}] Сохранение: {item_data['name']}")
            if parser.save_to_database(item_data):
                saved_count += 1

        print("\n" + "=" * 60)
        print(f"🎉 ПАРСИНГ ЗАВЕРШЕН!")
        print(f"📊 Найдено карточек: {len(items_data)}")
        print(f"💾 Сохранено товаров: {saved_count}")
        print("=" * 60)

        return len(items_data), saved_count

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0


if __name__ == "__main__":
    run_steam_parsing()