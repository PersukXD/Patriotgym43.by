from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
from app.models import Course


class CourseParser:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None

    def __enter__(self):
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()

    def setup_driver(self):
        """Настройка Chrome драйвера"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def close_driver(self):
        """Закрытие драйвера"""
        if self.driver:
            self.driver.quit()

    def wait_for_element(self, by, value, timeout=10):
        """Ожидание элемента"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def click_show_more_button(self):
        """Нажатие кнопки 'Показать ещё'"""
        try:
            # Ищем кнопку "Показать ещё"
            show_more_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-all-course"))
            )

            if show_more_button.is_displayed() and show_more_button.is_enabled():
                print("🔄 Нажимаем кнопку 'Показать ещё'...")

                # Прокручиваем к кнопке
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                           show_more_button)
                time.sleep(2)

                # Нажимаем кнопку с помощью JavaScript (более надежно)
                self.driver.execute_script("arguments[0].click();", show_more_button)

                # Ждем загрузки новых карточек
                time.sleep(3)

                # Дополнительное ожидание появления новых карточек
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "oneelemcurse"))
                )

                print("✅ Новые карточки загружены")
                return True
            else:
                print("⚠️ Кнопка 'Показать ещё' неактивна")
                return False

        except TimeoutException:
            print("❌ Кнопка 'Показать ещё' не найдена или время ожидания истекло")
            return False
        except Exception as e:
            print(f"❌ Ошибка при нажатии кнопки 'Показать ещё': {str(e)}")
            return False

    def get_all_course_cards(self, max_pages=3):
        """Получение всех карточек курсов с загрузкой дополнительных страниц"""
        all_cards = []
        current_page = 1

        print(f"🔍 Загружаем карточки с {max_pages} страниц...")

        while current_page <= max_pages:
            print(f"📄 Страница {current_page}:")

            # Ждем загрузки карточек
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "oneelemcurse"))
                )
            except TimeoutException:
                print("❌ Карточки курсов не найдены")
                break

            # Находим все карточки на текущей странице
            current_cards = self.driver.find_elements(By.CSS_SELECTOR,
                                                      ".col-lg-6.col-md-6.d-flex.align-items-stretch.oneelemcurse")

            print(f"   Найдено карточек: {len(current_cards)}")
            all_cards.extend(current_cards)

            # Если это не последняя страница, пытаемся загрузить следующую
            if current_page < max_pages:
                if not self.click_show_more_button():
                    print("🚫 Достигнут конец списка курсов")
                    break

            current_page += 1

        print(f"📊 Всего загружено карточек: {len(all_cards)}")
        return all_cards

    def parse_courses(self, limit=10, max_pages=2):
        """Основной метод парсинга курсов с поддержкой пагинации"""
        try:
            self.driver.get("https://patriot.rcek.by/courses")
            all_courses_data = []
            processed_urls = set()

            print("🎯 Начинаем парсинг курсов...")

            # Получаем все карточки с учетом пагинации
            all_cards = self.get_all_course_cards(max_pages=max_pages)

            if not all_cards:
                print("❌ Не удалось загрузить карточки курсов")
                return []

            # Ограничиваем общее количество обрабатываемых карточек
            if limit and len(all_cards) > limit:
                all_cards = all_cards[:limit]
                print(f"🎯 Ограничиваем обработку {limit} карточками")

            print(f"🔍 Будет обработано: {len(all_cards)} карточек")

            for i, card in enumerate(all_cards, 1):
                try:
                    print(f"\n📋 Обрабатываем карточку {i}/{len(all_cards)}")
                    course_data = self.parse_course_card(card, processed_urls)
                    if course_data:
                        all_courses_data.append(course_data)
                        print(f"✅ Карточка {i} успешно обработана: {course_data['title'][:50]}...")
                    else:
                        print(f"❌ Карточка {i} пропущена (дубликат или ошибка)")

                except Exception as e:
                    print(f"❌ Критическая ошибка при парсинге карточки {i}: {str(e)}")
                    continue

            print(f"\n🎯 Парсинг завершен! Собрано {len(all_courses_data)} из {len(all_cards)} курсов")

            # Диагностика
            if len(all_courses_data) < len(all_cards):
                print(f"🔍 Диагностика: {len(all_cards) - len(all_courses_data)} карточек не были обработаны")

            return all_courses_data

        except Exception as e:
            print(f"❌ Общая ошибка при парсинге: {str(e)}")
            import traceback
            print(f"🔍 Детали ошибки: {traceback.format_exc()}")
            return []

    def parse_course_card(self, card, processed_urls):
        """Парсинг отдельной карточки курса"""
        try:
            # Обновляем поиск элемента, т.к. страница могла измениться
            try:
                title_element = card.find_element(By.CSS_SELECTOR, "h3 a")
                title = title_element.text.strip()
                course_url = title_element.get_attribute("href")
            except StaleElementReferenceException:
                print("   ⚠️ Элемент устарел, пропускаем карточку")
                return None

            print(f"   📖 Название: {title[:30]}...")
            print(f"   🔗 URL: {course_url}")

            # Проверяем, не парсили ли мы уже этот курс
            if course_url in processed_urls:
                print(f"   ⚠️ Пропускаем дубликат: {course_url}")
                return None

            processed_urls.add(course_url)

            # Парсим дату
            try:
                date_element = card.find_element(By.CSS_SELECTOR, "h4")
                date_range = date_element.text.strip()
                print(f"   📅 Дата: {date_range}")
            except NoSuchElementException:
                date_range = ""
                print(f"   📅 Дата: не найдена")

            # Парсим изображение
            try:
                img_element = card.find_element(By.CSS_SELECTOR, "img.img-fluid")
                image_url = img_element.get_attribute("src")
                print(f"   🖼️ Изображение: найдено")
            except NoSuchElementException:
                image_url = ""
                print(f"   🖼️ Изображение: не найдено")

            # Проверяем наличие плашки о завершении мероприятия
            is_completed = False
            try:
                completed_element = card.find_element(By.CSS_SELECTOR, ".endcoursetoday")
                if completed_element:
                    is_completed = True
                    print(f"   ✅ Курс завершен")
            except NoSuchElementException:
                pass

            # Переходим на страницу курса для получения детальной информации
            print(f"   🔍 Переходим к парсингу деталей...")
            detail_data = self.parse_course_details(course_url)

            course_data = {
                'title': title,
                'date_range': date_range,
                'image_url': image_url,
                'is_completed': is_completed,
                'url': course_url,
                'description': detail_data.get('description', ''),
                'additional_info': detail_data.get('additional_info', ''),
                'organizers': detail_data.get('organizers', ''),
            }

            print(f"   ✅ Детали успешно получены")
            return course_data

        except Exception as e:
            print(f"❌ Ошибка при парсинге карточки: {str(e)}")
            import traceback
            print(f"🔍 Детали ошибки карточки: {traceback.format_exc()}")
            return None

    def parse_course_details(self, course_url):
        """Парсинг детальной информации о курсе - с активацией вкладок"""
        print(f"   🔍 Парсим детали курса: {course_url}")

        detail_data = {
            'description': '',
            'additional_info': '',
            'organizers': ''
        }

        try:
            original_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(course_url)

            # Увеличиваем время ожидания для динамического контента
            time.sleep(5)

            # 1. Парсим основное описание
            try:
                container_element = self.driver.find_element(By.CSS_SELECTOR, ".container.aos-init.aos-animate")
                detail_data['description'] = self.clean_text(container_element.text)
                print(f"   📝 Описание: {len(detail_data['description'])} символов")
            except NoSuchElementException:
                try:
                    description_element = self.driver.find_element(By.CLASS_NAME, "conseption")
                    detail_data['description'] = self.clean_text(description_element.text)
                    print(f"   📝 Описание (conseption): {len(detail_data['description'])} символов")
                except NoSuchElementException:
                    detail_data['description'] = ""
                    print("   📝 Описание: не найдено")

            # 2. Парсим дополнительную информацию с активацией вкладок
            additional_sections = []

            try:
                # Ждем загрузки блока с вкладками
                courserowcust_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "courserowcust"))
                )
                print("   ✅ Найден блок courserowcust")

                # Прокручиваем к блоку вкладок
                self.driver.execute_script("arguments[0].scrollIntoView(true);", courserowcust_element)
                time.sleep(2)

                # Пробуем кликнуть по каждой вкладке чтобы активировать контент
                for i in range(1, 4):
                    try:
                        # Находим ссылку вкладки и кликаем по ней
                        tab_link = self.driver.find_element(By.CSS_SELECTOR, f"a[href='#tab-{i}']")
                        self.driver.execute_script("arguments[0].click();", tab_link)
                        print(f"      🔄 Активирована вкладка {i}")
                        time.sleep(2)  # Ждем загрузки контента

                        # Теперь парсим контент вкладки
                        tab_content = self.driver.find_element(By.CSS_SELECTOR, f"#tab-{i} .details")
                        tab_text = self.clean_text(tab_content.text)

                        if tab_text and len(tab_text) > 10:
                            tab_names = ["📍 Месца правядзення", "👥 Удзельнікі", "📞 Кантакты"]
                            additional_sections.append(f"{tab_names[i - 1]}:\n{tab_text}")
                            print(f"      ✅ Вкладка {i}: найдено - {len(tab_text)} символов")
                        else:
                            print(f"      ⚠️ Вкладка {i}: текст пустой")

                    except Exception as e:
                        print(f"      ❌ Ошибка вкладки {i}: {e}")

            except Exception as e:
                print(f"   ❌ Ошибка блока вкладок: {e}")

            # Объединяем дополнительную информацию
            if additional_sections:
                detail_data['additional_info'] = '\n\n'.join(additional_sections)
                print(f"   📊 Доп.инфо: {len(detail_data['additional_info'])} символов")
            else:
                detail_data['additional_info'] = ""
                print("   📊 Доп.инфо: не найдено")

            # 3. Парсим организаторов
            organizers_list = []

            try:
                organizers_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".row.partrow"))
                )
                print("   ✅ Найден блок partrow")

                # Прокручиваем к блоку организаторов
                self.driver.execute_script("arguments[0].scrollIntoView(true);", organizers_section)
                time.sleep(2)

                # Ищем все изображения и ссылки организаторов
                org_blocks = organizers_section.find_elements(By.CSS_SELECTOR, ".col-lg-3")
                print(f"      Найдено блоков организаторов: {len(org_blocks)}")

                for block in org_blocks:
                    try:
                        # Ищем ссылку в блоке
                        link = block.find_element(By.CSS_SELECTOR, "a")
                        org_name = self.clean_text(link.text)
                        org_url = link.get_attribute('href')

                        if org_name and len(org_name) > 2:
                            if org_url:
                                organizers_list.append(f"🏢 {org_name} - {org_url}")
                            else:
                                organizers_list.append(f"🏢 {org_name}")
                            print(f"      ✅ Организатор: {org_name}")

                    except NoSuchElementException:
                        continue

            except Exception as e:
                print(f"   ❌ Ошибка блока организаторов: {e}")

            if organizers_list:
                detail_data['organizers'] = '\n'.join(organizers_list)
                print(f"   🏢 Организаторы: найдено {len(organizers_list)} организаторов")
            else:
                detail_data['organizers'] = ""
                print("   🏢 Организаторы: не найдено")

            # Закрываем вкладку и возвращаемся
            self.driver.close()
            self.driver.switch_to.window(original_window)

            print(f"   ✅ Детали успешно спарсены для {course_url}")
            return detail_data

        except Exception as e:
            print(f"   ❌ Ошибка при парсинге деталей курса {course_url}: {str(e)}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(original_window)
            except:
                pass
            return detail_data

    def clean_text(self, text):
        """Очищает текст от лишних пробелов и переносов"""
        if not text:
            return ""
        # Убираем лишние пробелы и переносы
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)


def save_courses_to_db(courses_data):
    """Сохранение курсов в базу данных"""
    saved_count = 0

    print(f"💾 Начинаем сохранение {len(courses_data)} курсов в базу...")

    for i, course_data in enumerate(courses_data, 1):
        try:
            print(f"📦 Сохраняем курс {i}/{len(courses_data)}: {course_data['title'][:50]}...")

            # Создаем или обновляем курс
            course, created = Course.objects.get_or_create(
                url=course_data['url'],
                defaults={
                    'title': course_data['title'],
                    'date_range': course_data['date_range'],
                    'image_url': course_data['image_url'],
                    'is_completed': course_data['is_completed'],
                    'description': course_data['description'],
                    'additional_info': course_data['additional_info'],
                    'organizers': course_data['organizers'],
                }
            )

            if created:
                saved_count += 1
                print(f"   ✅ Курс успешно создан (ID: {course.id})")
            else:
                # Обновляем существующий курс
                course.title = course_data['title']
                course.date_range = course_data['date_range']
                course.image_url = course_data['image_url']
                course.is_completed = course_data['is_completed']
                course.description = course_data['description']
                course.additional_info = course_data['additional_info']
                course.organizers = course_data['organizers']
                course.save()
                print(f"   🔄 Курс обновлен (ID: {course.id})")

        except Exception as e:
            print(f"   ❌ Ошибка при сохранении курса {course_data['title']}: {str(e)}")
            continue

    print(f"💾 Сохранение завершено! Успешно сохранено: {saved_count}/{len(courses_data)} курсов")
    return saved_count