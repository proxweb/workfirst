# Generated by Django 4.2.16 on 2024-11-20 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_alter_book_name_book'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='borrowed_book',
        ),
        migrations.RemoveField(
            model_name='book',
            name='user',
        ),
    ]
