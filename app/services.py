from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import time
import random


class ChromeWikiwayParser:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.wait = None
        self.base_url = "https://wikiway.com"

    def __enter__(self):
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def setup_driver(self):
        """Настройка Chrome WebDriver"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 30)
        except Exception as e:
            print(f"Ошибка при запуске Chrome: {e}")
            raise

    def _get_best_quality_url(self, image_url):
        """Получение URL изображения в лучшем качестве"""
        # Заменяем превью на оригиналы если возможно
        if '/resize_cache/' in image_url:
            # Пытаемся найти оригинал без ресайза
            original_url = image_url.replace('/resize_cache/', '/').replace('/200_150_2/', '/')
            return original_url
        return image_url
    def wait_for_cloudflare(self):
        """Ожидание прохождения CloudFlare проверки"""
        print("Ожидаем прохождения CloudFlare проверки...")

        for i in range(60):
            time.sleep(1)
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()

            if "just a moment" in page_source or "checking your browser" in page_source:
                print(f"CloudFlare проверка... ({i + 1}/60)")
                continue
            elif "challenge" in page_source or "captcha" in page_source:
                print("Обнаружена CAPTCHA! Пожалуйста, решите ее вручную в браузере...")
                input("Нажмите Enter после решения CAPTCHA...")
                break
            elif "wikiway.com/belarus/photo" in current_url and "just a moment" not in page_source:
                print("CloudFlare пройден! Загружаем контент...")
                break
            else:
                print(f"Загрузка... ({i + 1}/60) - URL: {current_url}")

        time.sleep(3)

    def solve_cloudflare_manually(self):
        """Ручное решение CloudFlare"""
        print("\n" + "=" * 50)
        print("⚠️  ТРЕБУЕТСЯ РУЧНОЕ ВМЕШАТЕЛЬСТВО!")
        print("Решите CAPTCHA 'Я не робот' в открывшемся браузере")
        print("После загрузки страницы с фотографиями нажмите Enter здесь")
        print("=" * 50 + "\n")
        input("Нажмите Enter после решения CAPTCHA...")

    def parse_wikiway_photos(self, url, max_images=50):
        """Парсинг фотографий с улучшенной фильтрацией"""
        try:
            print(f"Открываем страницу: {url}")
            self.driver.get(url)

            self.wait_for_cloudflare()

            if "just a moment" in self.driver.page_source.lower():
                self.solve_cloudflare_manually()

            current_url = self.driver.current_url
            if "wikiway.com/belarus/photo" not in current_url:
                print(f"Предупреждение: Текущий URL: {current_url}")

            print("Начинаем парсинг изображений...")
            time.sleep(3)

            # Прокручиваем страницу
            self._scroll_page()

            # Ищем изображения с улучшенной фильтрацией
            images_data = self._extract_wikiway_images_improved(max_images)

            print(f"Найдено {len(images_data)} изображений")
            return images_data

        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            return []

    def _scroll_page(self):
        """Прокрутка страницы"""
        print("Начинаем прокрутку страницы...")

        for i in range(3):
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_amount = scroll_height * (i + 1) // 4

            self.driver.execute_script(f"window.scrollTo(0, {scroll_amount});")
            time.sleep(random.uniform(1, 2))
            print(f"Прокрутка {i + 1}/3")

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def _extract_wikiway_images_improved(self, max_images):
        """Улучшенное извлечение изображений - ищем конкретно большие фото"""
        images_data = []

        print("Ищем изображения с улучшенной фильтрацией...")

        # Специфические селекторы для целевых изображений
        target_selectors = [
            # Основные большие изображения
            "img[src*='/upload/resize_cache/']",
            "img[data-src*='/upload/resize_cache/']",
            "img[src*='/upload/hl-photo/']",
            "img[data-src*='/upload/hl-photo/']",
            "img[loading='lazy']",  # Lazy loading изображения обычно основные
            ".photo-item img",
            ".gallery-item img",
            ".image-block img",
            "figure img",
            ".content img[src*='/upload/']",
        ]

        all_target_images = []

        for selector in target_selectors:
            try:
                images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Селектор '{selector}': найдено {len(images)} изображений")
                all_target_images.extend(images)
            except Exception as e:
                print(f"Ошибка с селектором {selector}: {e}")
                continue

        # Если не нашли целевые изображения, ищем все и фильтруем
        if not all_target_images:
            print("Целевые изображения не найдены, ищем все изображения...")
            all_target_images = self.driver.find_elements(By.TAG_NAME, "img")

        print(f"Всего кандидатов: {len(all_target_images)}")

        # Фильтруем изображения
        for img in all_target_images:
            if len(images_data) >= max_images:
                break

            try:
                src = img.get_attribute('src') or ''
                data_src = img.get_attribute('data-src') or ''
                alt = img.get_attribute('alt') or ''

                # Используем data-src для lazy loading, иначе src
                image_url = data_src if data_src else src

                if not image_url:
                    continue

                # Пропускаем data URI и пустые URL
                if image_url.startswith('data:'):
                    continue

                # Нормализуем URL
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url.startswith('/'):
                    image_url = urljoin(self.base_url, image_url)

                # Улучшенная фильтрация - ищем только целевые изображения
                if not self._is_target_image(image_url, img):
                    continue

                # Получаем размеры
                width = img.get_attribute('width') or ''
                height = img.get_attribute('height') or ''

                # Проверяем размеры
                try:
                    img_width = int(width) if width and width.isdigit() else 0
                    img_height = int(height) if height and height.isdigit() else 0

                    # Пропускаем слишком маленькие изображения
                    if img_width > 0 and img_height > 0:
                        if img_width < 200 or img_height < 150:
                            continue
                except:
                    pass

                # Получаем стили
                style = img.get_attribute('style') or ''
                style_width = self._extract_style_value(style, 'width')
                style_height = self._extract_style_value(style, 'height')

                # Создаем заголовок
                title = alt if alt and alt.strip() else f"Фото Беларуси {len(images_data) + 1}"

                images_data.append({
                    'title': title[:255],
                    'alt_text': alt,
                    'original_src': src,
                    'data_src': data_src,
                    'image_url': image_url,
                    'width': img_width if img_width > 0 else None,
                    'height': img_height if img_height > 0 else None,
                    'style_width': style_width,
                    'style_height': style_height,
                })

                print(f"✅ Целевое изображение: {title}")
                print(f"   URL: {image_url}")
                if img_width > 0:
                    print(f"   Размер: {img_width}x{img_height}")

            except Exception as e:
                print(f"❌ Ошибка при обработке изображения: {e}")
                continue

        return images_data

    def _is_target_image(self, image_url, img_element):
        """Проверяем, является ли изображение целевым (большим фото)"""
        # Целевые пути для изображений
        target_paths = [
            '/upload/resize_cache/',
            '/upload/hl-photo/',
            '/upload/iblock/',
            '/upload/uf/'
        ]

        # Пропускаем служебные изображения
        exclude_keywords = [
            'icon', 'logo', 'pixel', 'spacer', 'blank', 'placeholder',
            'avatar', 'thumb', 'small', 'mini', 'preview'
        ]

        # Проверяем путь
        is_target_path = any(path in image_url for path in target_paths)

        # Проверяем что НЕ является служебным
        is_not_service = not any(keyword in image_url.lower() for keyword in exclude_keywords)

        # Проверяем размер через JavaScript
        try:
            natural_width = img_element.get_attribute('naturalWidth')
            natural_height = img_element.get_attribute('naturalHeight')
            if natural_width and natural_height:
                if int(natural_width) >= 300 and int(natural_height) >= 200:
                    return True
        except:
            pass

        return is_target_path and is_not_service

    def _extract_style_value(self, style, property_name):
        """Извлечение значения свойства из style атрибута"""
        try:
            properties = style.split(';')
            for prop in properties:
                if property_name in prop:
                    return prop.split(':')[1].strip()
        except:
            pass
        return ""

    def close(self):
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()