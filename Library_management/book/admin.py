
from django.contrib import admin

from .models import *

admin.site.register(Book)
admin.site.register(BookInstance)
admin.site.register(Category)
# Register your models here.
