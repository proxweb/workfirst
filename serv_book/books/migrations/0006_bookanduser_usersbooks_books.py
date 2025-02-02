# Generated by Django 4.2.16 on 2024-11-20 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_remove_book_borrowed_book_remove_book_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookAndUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('received_date', models.DateField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_users', to='books.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_books', to='books.usersbooks')),
            ],
        ),
        migrations.AddField(
            model_name='usersbooks',
            name='books',
            field=models.ManyToManyField(related_name='borrowers', through='books.BookAndUser', to='books.book'),
        ),
    ]
