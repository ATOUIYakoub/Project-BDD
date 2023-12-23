from django.urls import path
from . import views


app_name = 'book'
urlpatterns = [
    path('home/<page_number>/', views.home, name='home'),
    path('home/<id>/<page_number>', views.home, name="home"),
    path('home/<user_id>/book/<book_id>', views.single, name='single'),
    path('book/<book_id>', views.single, name='single'),
    path('book/borrow/<book_id>', views.borrow, name='borrow'),
    path('book/<book_id>/borrow/<user_id>', views.borrow, name='borrow'),
    path('book/<book_id>/return_back/<user_id>',
         views.return_back, name='return_back'),
    path('book/<id>/search/<page_number>', views.search, name='search'),
    path('book/<id>/categories/<name>/<page_number>',
         views.categories, name='categories'),
    path('search/<page_number>', views.search, name='search'),
    path('categories/<name>/<page_number>',
         views.categories, name='categories'),

]
