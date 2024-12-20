from django.db import models



class UsersBooks(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30)
    mailuser = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=13, unique=True)
    books = models.ManyToManyField('Book', through='BookAndUser', related_name='borrowers', blank=True)

    def __str__(self):
        return f'{self.lastname} {self.firstname} {self.patronymic}'


class Book(models.Model):
    name_book = models.CharField(max_length=30, unique=True)
    author_book = models.CharField(max_length=30)
    publis_date = models.DateField('date of publication')
    quantity = models.PositiveIntegerField(default=1)   
    
    def __str__(self):
        return f'{self.name_book} - {self.author_book}'


class BookAndUser(models.Model):
    user = models.ForeignKey(UsersBooks, on_delete=models.CASCADE, related_name='user_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_users')
    received_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname} borrowed {self.book.name_book} on {self.received_date}"


class StoryBook(models.Model):
    user = models.ForeignKey(UsersBooks, on_delete=models.CASCADE, related_name='story_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='story_books')
    begin_date = models.DateField('Дата получения пользователем')
    end_date = models.DateField('Дата возврата пользователем')

    def __str__(self):
        return f"{self.user} взял {self.book} с {self.begin_date}"
