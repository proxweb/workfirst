# Generated by Django 4.2.16 on 2024-11-18 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_alter_book_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='name_book',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]