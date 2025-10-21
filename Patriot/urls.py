# Patriot/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app import views
from django.contrib.auth import views as auth_views
from app.views import GalleryView, historical_map, get_region_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('run-parser/', views.run_parser, name='run_parser'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),  # ДОБАВЬТЕ ЭТУ СТРОЧКУ!
    path('search/', views.search_news, name='search_news'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.user_profile_view, name='user_profile'),
    path('create-post/', views.create_post, name='create_post'),
    path('feed/', views.feed_view, name='feed'),
    # path('add-friend/<str:username>/', views.add_friend, name='add_friend'),  #pass
    path('feed/create-post/', views.create_post_from_feed, name='create_post_from_feed'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    path('historical-map/', views.historical_map, name='historical_map'),
    path('api/region/<int:region_id>/', get_region_data, name='get_region_data'),
    path('parse-courses/', views.run_courses_parser, name='parse_courses'),
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    # ДОБАВЛЕННЫЕ URL ДЛЯ АЛМАЗОВ
    path('api/diamonds/', views.get_user_diamonds, name='get_user_diamonds'),
    path('api/update_diamonds/', views.update_diamonds, name='update_diamonds'),
    path('api/quest-history/', views.get_quest_history, name='get_quest_history'),
    #магазин
    path('shop/', views.shop_view, name='shop'),
    path('api/buy-item/<int:item_id>/', views.buy_item, name='buy_item'),
    path('api/equip-item/<int:item_id>/', views.equip_item, name='equip_item'),
    path('api/unequip-item/<int:item_id>/', views.unequip_item, name='unequip_item'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('parse-steam/', views.run_steam_parser, name='parse_steam'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)