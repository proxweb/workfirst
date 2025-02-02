# Generated by Django 4.2.16 on 2024-11-21 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_alter_usersbooks_books'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersbooks',
            name='books',
            field=models.ManyToManyField(blank=True, related_name='borrowers', through='books.BookAndUser', to='books.book'),
        ),
    ]
