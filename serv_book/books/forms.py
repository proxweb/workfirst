from django import forms
from .models import Book, UsersBooks
from django.forms import modelformset_factory


class FormTableBook(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name_book', 'author_book', 'publis_date', 'quantity']


BookFormSet = modelformset_factory(Book, form=FormTableBook, extra=0)


class FormTableUser(forms.ModelForm):
    class Meta:
        model = UsersBooks
        fields = ['firstname', 'lastname', 'patronymic', 'mailuser', 'phone_number']

UserFormSet = modelformset_factory(UsersBooks, form=FormTableUser, extra=0)


class ItemForm(forms.Form):
    CATEGORY_CHOICES = [
        ('', 'Выберите категорию'),
        ('UsersBooks', 'Пользователи'),
        ('Book', 'Книги')
    ]

    BOOK_CHOICES = [
        ('', 'Выберите категорию поиска по книгам'),
        ('name_book', 'Книга'),
        ('author_book', 'Автор')
    ]

    UsersBooks_CHOICES = [
        ('', 'Выберите категорию поиска по пользователям'),
        ('firstname', 'Имя'),
        ('lastname', 'Фамилия'),
        ('patronymic', 'Отчество'),
        ('phone_number', 'Номер телефона'),
        ('mailuser', 'Email - почта')
    ]

    CATEGORY_FIND_CH = [
        ('icontains', 'Поиск по-любому совпадению'),
        ('contains', 'Поиск по-любому совпадению с учетом регистра'),
        ('iexact', 'Точное совпадение'),
        ('exact', 'Точное совпадение с учетом регистра'),
        ('istartswith', 'Поиск с начала строки данных'),
        ('startswith', 'Поиск с начала строки данных с учетом регистра'),
        ('iendswith', 'Поиск с конца строки данных'),
        ('endswith', 'Поиск с конца строки данных с учтом регистра'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=True, label="Выберите базу поиска", widget=forms.Select(attrs={'id': 'id_category'}))
    book_cat = forms.ChoiceField(choices=BOOK_CHOICES, required=False, label="Категория поиска по книгам", widget=forms.Select(attrs={'id': 'id_book_cat'}))
    user_cat = forms.ChoiceField(choices=UsersBooks_CHOICES, required=False, label="Категория поиска по пользователям", widget=forms.Select(attrs={'id': 'id_user_cat'}))
    text = forms.CharField(min_length=2, max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Поисковая строка'}))
    
    find_cat_0 = forms.ChoiceField(choices=CATEGORY_FIND_CH, required=True, label="Тип поиска")
    find_cat_1 = forms.ChoiceField(choices=CATEGORY_FIND_CH, required=False, label="Дополнительный тип фильтрации")
    find_cat_2 = forms.ChoiceField(choices=CATEGORY_FIND_CH, required=False, label="Дополнительный тип фильтрации")
    find_cat_3 = forms.ChoiceField(choices=CATEGORY_FIND_CH, required=False, label="Дополнительный тип фильтрации")

    date_from = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}), label="Дата с")
    date_to = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}), label="Дата по")

    def clean(self):
        cleaned_data = super().clean()
        find_cats = set()
        find_cat_0 = cleaned_data.get('find_cat_0')
        find_cats.add(find_cat_0)
        
        for i in range(1, 4):
            find_cat = cleaned_data.get(f'find_cat_{i}')
            if find_cat and find_cat in find_cats:
                raise forms.ValidationError("Типы поиска не могут повторяться.")
            find_cats.add(find_cat)
        
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Дата 'с' не может быть позже даты 'по'.")
        
        return cleaned_data