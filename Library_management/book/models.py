from django.db import models
# from Library_management.account.models import User
import datetime
# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=80)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    author = models.CharField(max_length=150, default='No Info')
    quantity = models.IntegerField(default=1)
    thumbnail = models.ImageField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_category(self):
        category = Category.objects.get(self.category)
        return category.name


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class BookInstance(models.Model):

    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    borrower = models.ForeignKey("account.User", on_delete=models.CASCADE)
    due_back = models.DateTimeField(
        default=datetime.datetime.utcnow() + datetime.timedelta(days=15))
    loan_status = models.BooleanField(default=True)
