from django.urls import path
from . import views


app_name = 'account'
urlpatterns = [
    path('<id>', views.profile, name='profile'),
    path('login/', views.login, name='login'),
    path('signup/', views.register, name='register'),
    path('info/<id>', views.info, name='info'),
    path('edit/<id>', views.edit, name='edit'),
    path('book_edit/<user_id>/<book_id>', views.book_edit, name='book_edit'),
    path('all_books/<user_id>', views.all_books, name='all_books'),
    path('all_books/<user_id>/<book_id>', views.all_books, name='all_books'),
    path('all_users/<user_id>', views.all_users, name='all_users'),
    path('all_users/<user_id>/<del_id>', views.all_users, name='all_users'),
    path('add_user/<user_id>', views.add_user, name='add_user'),
    path('add_book/<user_id>', views.add_book, name='add_book'),
    path('add_category/<user_id>', views.add_category, name='add_category'),
    path('change_avatar/<id>', views.change_avatar, name='change_avatar'),
    path('change_avatar/<id>', views.change_avatar, name='change_avatar'),
    path('change_pass/<id>', views.change_pass, name='change_pass'),
    path('logout/<user_id>', views.logout, name='logout'),


]
