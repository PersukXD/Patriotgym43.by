from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import PatriotNews, UserProfile, Post, Like, Comment, HistoricalRegion, Course, UserQuest, ShopItem, \
    UserInventory
from .forms import CustomUserCreationForm, UserProfileForm, CommentForm
from django.views import View
from django.core.paginator import Paginator
from .forms import WikiwayParserForm
from .services import ChromeWikiwayParser  # Изменено здесь
from .models import WikiwayImage
from django.db.models import Q
from django.conf import settings
from .utils import extract_audio_cover
import time
from datetime import datetime
import re
import random
import json
from app.services_2 import CourseParser, save_courses_to_db
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.views.decorators.cache import never_cache


def refresh_quotes(request):
    """Возвращает новые случайные цитаты"""
    quotes = get_random_quotes(3)
    return JsonResponse({'quotes': quotes})

def get_random_quotes(count=3):
    """Возвращает список случайных цитат"""
    quotes = getattr(settings, 'PATRIOTIC_QUOTES', [
        "Будьте в курсе последних событий",
        "Участвуйте в патриотических акциях",
        "Любовь к Родине - основа воспитания",
    ])

    if len(quotes) <= count:
        return quotes

    return random.sample(quotes, count)


def home(request):
    news = PatriotNews.objects.all().order_by('-date')
    courses = Course.objects.all()[:4]  # Берем первые 4 курса для главной страницы

    # Получаем изображения для карусели (последние 5)
    carousel_images = WikiwayImage.objects.filter(is_parsed=True).order_by('-created_at')[:5]

    # Получаем случайные цитаты
    quotes = get_random_quotes(len(carousel_images) if carousel_images else 3)

    # Объединяем изображения с цитатами
    carousel_data = []
    for i, image in enumerate(carousel_images):
        quote = quotes[i % len(quotes)] if i < len(quotes) else quotes[-1]
        carousel_data.append({
            'image': image,
            'quote': quote,
            'author': 'Патриотическое воспитание'
        })

    # Если нет изображений, создаем заглушки с цитатами
    if not carousel_data:
        quotes = get_random_quotes(3)
        carousel_data = [
            {
                'image': type('MockImage', (), {
                    'get_display_url': '#',
                    'title': 'Цитата 1',
                    'alt_text': quotes[0]
                })(),
                'quote': quotes[0],
                'author': 'Патриотическое воспитание'
            },
            # ... остальные заглушки
        ]

    context = {
        'news': news,
        'courses': courses,  # Добавляем курсы в контекст
        'carousel_data': carousel_data,
    }
    return render(request, 'index.html', context)
def run_parser(request):
    if request.method == 'POST':
        try:
            from .parsing import run_parsing
            parsed_count, saved_count = run_parsing()
            messages.success(request, f'Парсинг завершен! Спарсено: {parsed_count}, Сохранено: {saved_count}')
        except Exception as e:
            messages.error(request, f'Ошибка при парсинге: {str(e)}')
        return redirect('home')
    return JsonResponse({'status': 'Use POST method'})


def news_list(request):
    news = PatriotNews.objects.all().order_by('-date')
    return render(request, 'news_list.html', {'news': news})


def news_detail(request, news_id):
    news_item = get_object_or_404(PatriotNews, id=news_id)

    context = {
        'news_item': news_item,
    }
    return render(request, 'news/news_detail.html', context)


def search_news(request):
    query = request.GET.get('q', '').strip()
    news_results = PatriotNews.objects.all()
    courses_results = Course.objects.all()

    if query:
        # Разбиваем запрос на слова и ищем каждое слово
        words = query.split()
        q_objects = Q()

        for word in words:
            q_objects |= Q(title__icontains=word)
            q_objects |= Q(text__icontains=word)

        news_results = news_results.filter(q_objects).order_by('-date')
        courses_results = courses_results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(additional_info__icontains=query)
        ).order_by('-created_at')

    # AJAX запрос для автозаполнения
    if request.GET.get('ajax') == '1':
        results = []

        # Добавляем новости в результаты
        for item in news_results[:3]:  # Ограничиваем до 3 новостей
            results.append({
                'title': item.title,
                'date': item.date.strftime('%d.%m.%Y'),
                'type': 'news',
                'url': f'/news/{item.id}/'  # URL для новости
            })

        # Добавляем курсы в результаты
        for item in courses_results[:2]:  # Ограничиваем до 2 курсов
            results.append({
                'title': item.title,
                'date': item.date_range,
                'type': 'course',
                'url': f'/courses/{item.id}/'  # URL для курса
            })

        return JsonResponse({'results': results})

    context = {
        'news_results': news_results,
        'courses_results': courses_results,
        'query': query,
        'total_results': news_results.count() + courses_results.count()
    }
    return render(request, 'search/search_results.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Создаем профиль, если его нет
                UserProfile.objects.get_or_create(user=user)

                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()

    # Очищаем старые сообщения при заходе на страницу входа
    storage = get_messages(request)
    for message in storage:
        pass  # Просто читаем все сообщения чтобы очистить их

    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()

    # Очищаем старые сообщения при заходе на страницу регистрации
    storage = get_messages(request)
    for message in storage:
        pass  # Просто читаем все сообщения чтобы очистить их

    return render(request, 'registration/register.html', {'form': form})


@never_cache
@login_required
def user_profile_view(request, username):
    """Просмотр профиля любого пользователя"""
    try:
        # Получаем пользователя по username
        profile_user = get_object_or_404(User, username=username)
        user_profile_obj, created = UserProfile.objects.get_or_create(user=profile_user)

        # Определяем, является ли профиль своим
        is_own_profile = request.user == profile_user

        # Получаем посты пользователя
        user_posts = Post.objects.filter(author=profile_user).order_by('-created_at')

        # Обработка изменения аватарки
        if request.method == 'POST' and is_own_profile:
            action = request.POST.get('action')

            if action == 'change_avatar':
                # Изменение аватарки
                if 'avatar' in request.FILES:
                    user_profile_obj.avatar = request.FILES['avatar']
                    user_profile_obj.save()
                    messages.success(request, 'Аватарка обновлена!')
                return redirect('user_profile', username=username)

            elif action == 'delete_avatar':
                # Удаление аватарки
                if user_profile_obj.avatar:
                    user_profile_obj.avatar.delete(save=False)
                    user_profile_obj.avatar = None
                    user_profile_obj.save()
                    messages.success(request, 'Аватарка удалена!')
                return redirect('user_profile', username=username)

            elif action == 'update_profile':
                # Обновление остальных полей профиля
                form = UserProfileForm(request.POST, instance=user_profile_obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Профиль обновлен!')
                    return redirect('user_profile', username=username)
            else:
                # Стандартное обновление профиля (для обратной совместимости)
                form = UserProfileForm(request.POST, request.FILES, instance=user_profile_obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Профиль обновлен!')
                    return redirect('user_profile', username=username)

        # Форма для редактирования (только для своего профиля)
        form = None
        if is_own_profile:
            form = UserProfileForm(instance=user_profile_obj)

        # Получаем доступные рамки и экипированные предметы
        available_frames = []
        equipped_items = []

        if is_own_profile:
            # Получаем рамки аватарок из инвентаря пользователя
            available_frames = UserInventory.objects.filter(
                user=request.user,
                item__category='avatar_frame'
            ).select_related('item')

            # Получаем экипированные предметы
            equipped_items = user_profile_obj.get_equipped_items()

            # Отладочная информация
            print("Активная рамка:", user_profile_obj.active_avatar_frame)
            print("Доступные рамки:", list(available_frames))
        else:
            # Для чужого профиля показываем только активные предметы
            equipped_items = user_profile_obj.get_equipped_items()

        context = {
            'user': profile_user,
            'profile': user_profile_obj,
            'posts': user_posts,
            'form': form,
            'friends_count': user_profile_obj.friends.count() if hasattr(user_profile_obj, 'friends') else 0,
            'posts_count': user_posts.count(),
            'is_own_profile': is_own_profile,
            'available_frames': available_frames,
            'equipped_items': equipped_items,
            'cache_buster': int(timezone.now().timestamp()),
        }

        return render(request, 'profile/profile.html', context)

    except User.DoesNotExist:
        messages.error(request, f'Пользователь {username} не найден.')
        return redirect('feed')

@login_required
def profile_view(request):
    """Собственный профиль пользователя - перенаправляем на общий шаблон профиля"""
    return user_profile_view(request, request.user.username)


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        post_type = request.POST.get('post_type', 'text')
        media_file = request.FILES.get('media_file')

        if content:
            Post.objects.create(
                author=request.user,
                content=content,
                post_type=post_type,
                media_file=media_file
            )
            messages.success(request, 'Пост опубликован!')
        else:
            messages.error(request, 'Текст поста не может быть пустым')

    return redirect('profile')


@login_required
def feed_view(request):
    posts = Post.objects.all().select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')
    comment_form = CommentForm()

    context = {
        'posts': posts,
        'comment_form': comment_form,
    }
    return render(request, 'feed/feed.html', context)


@login_required
def create_post_from_feed(request):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        post_type = request.POST.get('post_type', 'text')
        media_file = request.FILES.get('media_file')

        if content.strip():
            Post.objects.create(
                author=request.user,
                content=content,
                post_type=post_type,
                media_file=media_file
            )
            messages.success(request, 'Пост опубликован в ленте!')
        else:
            messages.error(request, 'Текст поста не может быть пустым')

    return redirect('feed')


@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        likes_count = post.likes.count()
        return JsonResponse({'likes_count': likes_count, 'liked': liked})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def add_comment(request, post_id):
    """Добавление комментария - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    try:
        post = get_object_or_404(Post, id=post_id)

        # Получаем данные из формы
        content = request.POST.get('content', '').strip()

        if not content:
            return JsonResponse({
                'success': False,
                'error': 'Комментарий не может быть пустым'
            }, status=400)

        # Создаем комментарий
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            content=content
        )

        return JsonResponse({
            'success': True,
            'user': comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
            'comments_count': post.comments.count(),
            'comment_id': comment.id,
            'can_delete': comment.user_can_delete(request.user)
        })

    except Exception as e:
        print(f"Error adding comment: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Внутренняя ошибка сервера при добавлении комментария'
        }, status=500)


# app/views.py
@require_http_methods(["POST"])
@csrf_exempt
@login_required
def delete_post(request, post_id):
    """Удаление поста - УПРОЩЕННАЯ ВЕРСИЯ"""
    try:
        post = get_object_or_404(Post, id=post_id)

        # Проверяем права на удаление
        if not post.user_can_delete(request.user):
            return JsonResponse({
                'success': False,
                'error': 'У вас нет прав для удаления этого поста'
            }, status=403)

        post.delete()

        return JsonResponse({
            'success': True,
            'message': 'Пост успешно удален'
        })

    except Exception as e:
        print(f"Error deleting post: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
@login_required
def delete_comment(request, comment_id):
    """Удаление комментария - УПРОЩЕННАЯ ВЕРСИЯ"""
    try:
        comment = get_object_or_404(Comment, id=comment_id)

        # Проверяем права на удаление
        if not comment.user_can_delete(request.user):
            return JsonResponse({
                'success': False,
                'error': 'У вас нет прав для удаления этого комментария'
            }, status=403)

        post_id = comment.post.id
        comments_count = comment.post.comments.count() - 1
        comment.delete()

        return JsonResponse({
            'success': True,
            'comments_count': comments_count,
            'message': 'Комментарий успешно удален'
        })

    except Exception as e:
        print(f"Error deleting comment: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }, status=500)
# Временная заглушка для функции добавления друга
@login_required
def add_friend(request, username):
    messages.info(request, 'Функция добавления друзей скоро будет доступна!')
    return redirect('profile')


class GalleryView(View):
    template_name = 'gallery.html'

    def get(self, request):
        form = WikiwayParserForm()

        # Получаем все изображения (теперь не нужно проверять local_image)
        images = WikiwayImage.objects.all().order_by('-created_at')

        # Пагинация
        paginator = Paginator(images, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Статистика
        total_images = WikiwayImage.objects.count()

        context = {
            'form': form,
            'images': page_obj,
            'total_images': total_images,
            'downloaded_count': total_images,  # Теперь все изображения "скачаны"
            'not_downloaded_count': 0,  # Больше нет нескачанных
        }

        return render(request, self.template_name, context)

    def post(self, request):
        form = WikiwayParserForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']
            max_images = form.cleaned_data['max_images']

            try:
                # Парсим изображения
                with ChromeWikiwayParser(headless=False) as parser:
                    images_data = parser.parse_wikiway_photos(url, max_images)

                if not images_data:
                    messages.warning(request, 'Не найдено изображений для сохранения')
                    return redirect('gallery')

                saved_count = 0

                for img_data in images_data:
                    try:
                        # Создаем запись в базе данных (без скачивания)
                        image_obj, created = WikiwayImage.objects.get_or_create(
                            image_url=img_data['image_url'],
                            defaults={
                                'title': img_data['title'],
                                'alt_text': img_data['alt_text'],
                                'original_src': img_data['original_src'],
                                'data_src': img_data['data_src'],
                                'width': img_data['width'],
                                'height': img_data['height'],
                                'style_width': img_data['style_width'],
                                'style_height': img_data['style_height'],
                                'is_parsed': True,
                            }
                        )

                        if created:
                            saved_count += 1

                    except Exception as e:
                        print(f"Ошибка при сохранении изображения: {e}")
                        continue

                messages.success(
                    request,
                    f'Успешно сохранено {saved_count} изображений (ссылки)'
                )

            except Exception as e:
                messages.error(request, f'Ошибка при парсинге: {str(e)}')

            return redirect('gallery')

        # Если форма не валидна
        return self.get(request)


@login_required
def historical_map(request):
    """Карта доступна только авторизованным пользователям"""
    # Получаем все периоды для фильтрации
    periods = HistoricalRegion.PERIOD_CHOICES
    current_period = request.GET.get('period', 'all')

    if current_period != 'all':
        regions = HistoricalRegion.objects.filter(period=current_period, is_active=True)
    else:
        regions = HistoricalRegion.objects.filter(is_active=True)

    # Подготавливаем данные для карты
    regions_data = []
    for region in regions:
        regions_data.append({
            'id': region.id,
            'name': region.name,
            'center_lat': region.center_lat,
            'center_lng': region.center_lng,
            'coordinates': region.coordinates,
            'period': region.period,
            'category': region.category,
            'icon': region.get_category_icon(),
        })

    # Получаем данные пользователя для передачи в шаблон
    user_profile = request.user.userprofile
    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'diamonds': user_profile.diamonds
    }

    context = {
        'regions': regions,
        'regions_json': json.dumps(regions_data, ensure_ascii=False),
        'periods': periods,
        'current_period': current_period,
        'categories': dict(HistoricalRegion._meta.get_field('category').choices),
        'user_data': user_data,
    }
    return render(request, 'historical_map/map.html', context)


def get_region_data(request, region_id):
    """API для получения данных о регионе"""
    try:
        region = HistoricalRegion.objects.get(id=region_id)
        data = {
            'id': region.id,
            'name': region.name,
            'description': region.description,
            'stories': region.get_stories_list(),
            'period': region.get_period_display(),
            'year': region.year,
            'category': region.get_category_display(),
            'icon': region.get_category_icon(),
            'image_url': region.image.url if region.image else '',
        }
        return JsonResponse(data)
    except HistoricalRegion.DoesNotExist:
        return JsonResponse({'error': 'Region not found'}, status=404)


# Добавьте в views.py

def run_courses_parser(request, app=None):
    """Запуск парсера курсов"""
    if request.method == 'POST':
        try:
            from app.services import CourseParser, save_courses_to_db

            with CourseParser(headless=True) as parser:
                courses_data = parser.parse_courses()

            saved_count = save_courses_to_db(courses_data)

            messages.success(
                request,
                f'Парсинг курсов завершен! Спарсено: {len(courses_data)}, Сохранено: {saved_count}'
            )

        except Exception as e:
            messages.error(request, f'Ошибка при парсинге курсов: {str(e)}')

        return redirect('home')

    return JsonResponse({'status': 'Use POST method'})


# Добавьте в views.py после существующих импортов


# Добавьте эти функции в views.py

def run_courses_parser(request):
    """Запуск парсера курсов"""
    if request.method == 'POST':
        try:
            with CourseParser(headless=True) as parser:
                courses_data = parser.parse_courses()

            saved_count = save_courses_to_db(courses_data)

            messages.success(
                request,
                f'Парсинг курсов завершен! Спарсено: {len(courses_data)}, Сохранено: {saved_count}'
            )

        except Exception as e:
            messages.error(request, f'Ошибка при парсинге курсов: {str(e)}')

        return redirect('home')

    return JsonResponse({'status': 'Use POST method'})


from datetime import datetime


def courses_list(request):
    """Список курсов"""
    courses = list(Course.objects.all())

    def get_relevance_score(course):
        """Определяет релевантность мероприятия"""
        date_range = course.date_range or ""
        now = datetime.now()

        # Словарь месяцев
        months = {
            'января': '01', 'февраля': '02', 'марта': '03',
            'апреля': '04', 'мая': '05', 'июня': '06',
            'июля': '07', 'августа': '08', 'сентября': '09',
            'октября': '10', 'ноября': '11', 'декабря': '12'
        }

        try:
            dates = date_range.split('-')
            start_date = None
            end_date = None

            # Парсим начальную дату
            if len(dates) > 0:
                start_parts = dates[0].strip().split()
                if len(start_parts) == 3:
                    start_date = datetime(
                        int(start_parts[2]),
                        int(months.get(start_parts[1], 1)),
                        int(start_parts[0])
                    )

            # Парсим конечную дату
            if len(dates) > 1:
                end_parts = dates[1].strip().split()
                if len(end_parts) == 3:
                    end_date = datetime(
                        int(end_parts[2]),
                        int(months.get(end_parts[1], 1)),
                        int(end_parts[0])
                    )

            # НОВАЯ ЛОГИКА ПРИОРИТЕТОВ:
            # 1. Будущие мероприятия (еще не начались)
            # 2. Текущие мероприятия (сейчас идут)
            # 3. Завершенные мероприятия

            if end_date and start_date:
                if now < start_date:
                    # Будущее мероприятие - высший приоритет
                    return f"2_{start_date.strftime('%Y%m%d')}"
                elif start_date <= now <= end_date:
                    # Текущее мероприятие
                    return f"1_{end_date.strftime('%Y%m%d')}"
                else:
                    # Завершенное мероприятие
                    return f"0_{end_date.strftime('%Y%m%d')}"

        except Exception:
            pass

        return "0_00000000"

    # Сортируем по релевантности
    courses.sort(key=lambda x: get_relevance_score(x), reverse=True)

    context = {
        'courses': courses,
    }
    return render(request, 'courses/courses_list.html', context)


def course_detail(request, course_id):
    """Детальная страница курса"""
    course = get_object_or_404(Course, id=course_id)

    context = {
        'course': course,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def get_quest_history(request):
    """Получить историю выполненных заданий"""
    try:
        quests = UserQuest.objects.filter(user=request.user, completed=True).order_by('-completed_at')[:10]

        quests_data = []
        for quest in quests:
            quests_data.append({
                'quest_type': quest.quest_type,
                'difficulty': quest.difficulty,
                'diamonds_earned': quest.diamonds_earned,
                'completed_at': quest.completed_at.strftime('%d.%m.%Y %H:%M') if quest.completed_at else 'Неизвестно'
            })

        return JsonResponse({
            'success': True,
            'quests': quests_data,
            'total_quests': UserQuest.objects.filter(user=request.user, completed=True).count()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)



@login_required
def get_user_diamonds(request):
    """Получить количество алмазов пользователя - ОБНОВЛЕННАЯ ВЕРСИЯ"""
    try:
        # Принудительно получаем свежие данные из базы
        profile = UserProfile.objects.get(user=request.user)

        # Логируем для отладки
        print(f"🔍 Запрос алмазов для пользователя {request.user.username}: {profile.diamonds}")

        return JsonResponse({
            'success': True,
            'diamonds': profile.diamonds,
            'username': request.user.username,
            'user_id': request.user.id
        })
    except UserProfile.DoesNotExist:
        # Если профиля нет - создаем с нулевым балансом
        profile = UserProfile.objects.create(user=request.user, diamonds=0)
        print(f"🆕 Создан новый профиль для {request.user.username} с 0 алмазов")

        return JsonResponse({
            'success': True,
            'diamonds': 0,
            'username': request.user.username,
            'user_id': request.user.id
        })
    except Exception as e:
        print(f"❌ Ошибка при получении алмазов: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def update_diamonds(request):
    """Обновить количество алмазов пользователя - ОБНОВЛЕННАЯ ВЕРСИЯ"""
    try:
        data = json.loads(request.body)
        diamonds_to_add = data.get('diamonds', 0)
        quest_type = data.get('quest_type', 'general')
        difficulty = data.get('difficulty', 'medium')

        if diamonds_to_add <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Количество алмазов должно быть положительным'
            }, status=400)

        # Получаем или создаем профиль
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'diamonds': 0}
        )

        old_balance = profile.diamonds
        profile.diamonds += diamonds_to_add
        profile.save()

        # Принудительно обновляем объект из базы
        profile.refresh_from_db()

        # Сохраняем информацию о выполненном задании
        UserQuest.objects.create(
            user=request.user,
            quest_type=quest_type,
            difficulty=difficulty,
            completed=True,
            diamonds_earned=diamonds_to_add
        )

        print(f"💰 Пользователь {request.user.username}: {old_balance} + {diamonds_to_add} = {profile.diamonds}")

        return JsonResponse({
            'success': True,
            'old_balance': old_balance,
            'new_balance': profile.diamonds,
            'added': diamonds_to_add,
            'user_id': request.user.id
        })

    except Exception as e:
        print(f"❌ Ошибка при обновлении алмазов: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@never_cache
@login_required
def shop_view(request):
    """Страница магазина"""
    items = ShopItem.objects.filter(is_active=True).order_by('category', 'price')

    # Группируем товары по категориям
    categories = {}
    for item in items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)

    # Получаем инвентарь пользователя
    user_inventory = UserInventory.objects.filter(user=request.user).values_list('item_id', flat=True)

    context = {
        'categories': categories,
        'user_inventory': list(user_inventory),
        'user_diamonds': request.user.userprofile.diamonds,
        'cache_buster': int(timezone.now().timestamp()),
    }
    return render(request, 'shop/shop_new.html', context)


@login_required
@require_http_methods(["POST"])
def buy_item(request, item_id):
    """Покупка товара"""
    try:
        item = get_object_or_404(ShopItem, id=item_id, is_active=True)
        profile = request.user.userprofile

        # Проверяем, есть ли уже этот товар
        if UserInventory.objects.filter(user=request.user, item=item).exists():
            return JsonResponse({
                'success': False,
                'error': 'У вас уже есть этот товар'
            }, status=400)

        # Проверяем хватает ли алмазов
        if profile.diamonds < item.price:
            return JsonResponse({
                'success': False,
                'error': 'Недостаточно алмазов'
            }, status=400)

        # Списание алмазов
        profile.diamonds -= item.price
        profile.save()

        # Добавление в инвентарь
        UserInventory.objects.create(user=request.user, item=item)

        return JsonResponse({
            'success': True,
            'new_balance': profile.diamonds,
            'item_name': item.name,
            'item_id': item.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def equip_item(request, item_id):
    """Надеть предмет"""
    try:
        item = get_object_or_404(ShopItem, id=item_id, is_active=True)
        profile = request.user.userprofile

        # Проверяем, есть ли предмет в инвентаре пользователя
        user_inventory_item = get_object_or_404(
            UserInventory,
            user=request.user,
            item=item
        )

        # Снимаем все предметы той же категории
        equipped_items = UserInventory.objects.filter(
            user=request.user,
            item__category=item.category,
            is_equipped=True
        )

        for equipped_item in equipped_items:
            equipped_item.is_equipped = False
            equipped_item.save()

            # Также снимаем в профиле
            if item.category == 'avatar_frame' and profile.active_avatar_frame == equipped_item.item:
                profile.active_avatar_frame = None
            elif item.category == 'profile_background' and profile.active_profile_background == equipped_item.item:
                profile.active_profile_background = None
            elif item.category == 'badge' and profile.active_badge == equipped_item.item:
                profile.active_badge = None

        # Надеваем новый предмет
        user_inventory_item.is_equipped = True
        user_inventory_item.save()

        # Сохраняем в профиле
        if item.category == 'avatar_frame':
            profile.active_avatar_frame = item
        elif item.category == 'profile_background':
            profile.active_profile_background = item
        elif item.category == 'badge':
            profile.active_badge = item

        profile.save()

        return JsonResponse({
            'success': True,
            'item_name': item.name,
            'category': item.category,
            'message': 'Предмет успешно надет'
        })

    except UserInventory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'У вас нет этого предмета в инвентаре'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def unequip_item(request, item_id):
    """Снять предмет"""
    try:
        item = get_object_or_404(ShopItem, id=item_id)
        profile = request.user.userprofile

        # Проверяем, есть ли предмет в инвентаре и надет ли он
        user_inventory_item = get_object_or_404(
            UserInventory,
            user=request.user,
            item=item
        )

        if not user_inventory_item.is_equipped:
            return JsonResponse({
                'success': False,
                'error': 'Этот предмет не надет'
            }, status=400)

        # Снимаем предмет
        user_inventory_item.is_equipped = False
        user_inventory_item.save()

        # Снимаем в профиле
        if item.category == 'avatar_frame' and profile.active_avatar_frame == item:
            profile.active_avatar_frame = None
        elif item.category == 'profile_background' and profile.active_profile_background == item:
            profile.active_profile_background = None
        elif item.category == 'badge' and profile.active_badge == item:
            profile.active_badge = None

        profile.save()

        return JsonResponse({
            'success': True,
            'item_name': item.name,
            'category': item.category,
            'message': 'Предмет снят'
        })

    except UserInventory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'У вас нет этого предмета в инвентаре'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)




@never_cache
@login_required
def inventory_view(request):
    """Страница инвентаря (для модального окна)"""
    try:
        # Получаем инвентарь пользователя
        inventory_items = UserInventory.objects.filter(
            user=request.user
        ).select_related('item').order_by('item__category', 'item__name')

        # Группируем по категориям
        categories = {}
        for inv_item in inventory_items:
            category = inv_item.item.category
            if category not in categories:
                categories[category] = []
            categories[category].append(inv_item)

        # Отладочная информация
        print(f"🔍 Инвентарь пользователя {request.user.username}:")
        print(f"📦 Всего предметов: {inventory_items.count()}")
        for category, items in categories.items():
            print(f"   📁 {category}: {len(items)} предметов")
            for item in items:
                print(f"      🎯 {item.item.name} (ID: {item.item.id}), надето: {item.is_equipped}")

        context = {
            'user_diamonds': request.user.userprofile.diamonds,
            'equipped_items': request.user.userprofile.get_equipped_items(),
            'categories': categories,
            'inventory_items': inventory_items,  # Добавляем для отладки
            'cache_buster': int(timezone.now().timestamp()),
        }

        # Если это AJAX запрос для модального окна
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'shop/inventory_modal.html', context)

        return render(request, 'shop/inventory.html', context)

    except Exception as e:
        print(f"❌ Ошибка в inventory_view: {e}")
        # Возвращаем пустой контекст в случае ошибки
        context = {
            'categories': {},
            'inventory_items': [],
            'user_diamonds': 0,
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'shop/inventory_modal.html', context)
        return render(request, 'shop/inventory.html', context)


def run_steam_parser(request):
    """Запуск парсера Steam"""
    if request.method == 'POST':
        try:
            from .steam_parser import run_steam_parsing
            parsed_count, saved_count = run_steam_parsing()
            messages.success(request, f'Парсинг Steam завершен! Обработано: {parsed_count}, Сохранено: {saved_count}')
        except Exception as e:
            messages.error(request, f'аОшибка при парсинге Steam: {str(e)}')
        return redirect('shop')  # Перенаправляем в магазин

    return JsonResponse({'status': 'Use POST method'})