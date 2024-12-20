from django.contrib import admin
from .models import Book, UsersBooks, BookAndUser
# Register your models here.

admin.site.register(Book)
admin.site.register(UsersBooks)
admin.site.register(BookAndUser)