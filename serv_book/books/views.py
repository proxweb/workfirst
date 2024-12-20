from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
import pdfkit
from .forms import BookFormSet, FormTableBook, FormTableUser, UserFormSet, ItemForm
from .models import Book, UsersBooks, BookAndUser, StoryBook
from .serializers import BookSerializer


#REST API
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # permission_classes = (IsAuthenticated,)


# просмотр основых баз данных
class AllView(ListView):
    template_name = 'main.html'
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = UsersBooks.objects.all()
        return context


# детальная информация о пользователе
class UserDetailView(DetailView):

    model = UsersBooks
    template_name = 'work.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_users'] = BookAndUser.objects.filter(user=self.object).select_related('book')
        return context


# детальная информация о книге
class BookDetailView(DetailView):

    model = Book
    template_name = 'work.html'
    context_object_name = 'book'


# поисковая система по данным базы
def searchfunc(request):

    form_search = ItemForm(request.POST or None) 

    if request.method == 'POST' and form_search.is_valid(): 

        text = form_search.cleaned_data.get('text')
        status = f'Поиск по запросу {text} не дал никаких результатов в выбраной вами категории поиска'
        category = form_search.cleaned_data.get('category') 
        find_cat = (form_search.cleaned_data.get(f'find_cat_{i}') for i in range(4) if form_search.cleaned_data.get(f'find_cat_{i}'))

        date_from = form_search.cleaned_data.get('date_from') 
        date_to = form_search.cleaned_data.get('date_to')

        if category == 'UsersBooks':
            user_cat = form_search.cleaned_data['user_cat']
            mainusers = UsersBooks.objects.all()
            slov_up = {(getattr(user, user_cat)).upper():user.id for user in mainusers}
            for find_c in find_cat:
                if find_c[0] == 'i':
                    fil_id = filterfunc(slov_up, find_c, text)
                    mainusers = mainusers.filter(id__in=fil_id)
                else:
                    mainusers = mainusers.filter(**{f'{user_cat}__{find_c}':text})
            if date_from and date_to:
                    storybook = StoryBook.objects.filter(begin_date__gte=date_from, end_date__lte = date_to)
                    mainusers = mainusers.filter(id__in=storybook.values('user_id'))
            elif date_from:
                    storybook = StoryBook.objects.filter(begin_date__gte=date_from)
                    mainusers = mainusers.filter(id__in=storybook.values('user_id'))
            elif date_to:
                    storybook = StoryBook.objects.filter(end_date__lte = date_to)
                    mainusers = mainusers.filter(id__in=storybook.values('user_id'))
            else:
                storybook = StoryBook.objects.all()
            for user in mainusers:
                user.story = storybook.filter(user = user.id)
            
            return render(request, "page_search.html", {'users':mainusers, 'status':status, 'storybook':storybook})
             
        if category == 'Book':
            book_cat = form_search.cleaned_data['book_cat']
            mainbooks = Book.objects.all()
            slov_up = {(getattr(book, book_cat)).upper():book.id for book in mainbooks}
            for find_c in find_cat:
                if find_c == 'i':
                    fil_id = filterfunc(slov_up, find_c, text)
                    mainbooks = mainbooks.filter(id__in=fil_id)
                else:
                    mainbooks = mainbooks.filter(**{f'{book_cat}__{find_c}':text})
            if date_from and date_to:
                storybook = StoryBook.objects.filter(begin_date=date_from, end_date = date_to)
                mainbooks = mainbooks.filter(id__in=storybook.values('book_id'))
            elif date_from:
                storybook = StoryBook.objects.filter(begin_date=date_from)
                mainbooks = mainbooks.filter(id__in=storybook.values('book_id'))
            elif date_to:
                storybook = StoryBook.objects.filter(end_date = date_to)
                mainbooks = mainbooks.filter(id__in=storybook.values('book_id'))
            else:
                storybook = StoryBook.objects.all()
            for book in mainbooks:
                book.story = storybook.filter(book = book.id)
            return render(request, "page_search.html", {'books':mainbooks, 'status':status, 'storybook':storybook})

    return render(request, "page_search.html")


# создание ПДФ по результату фильтрации баз данных
def generate_pdf(request):

    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    
    if 'Books' in request.POST:
        selected_books_ids = request.POST.getlist('selected_books')
        books = Book.objects.filter(id__in=selected_books_ids)

        selected_stors_ids = request.POST.getlist('selected_stors')
        storybook = StoryBook.objects.filter(id__in=selected_stors_ids)
        for book in books:
            book.story = storybook.filter(book = book.id)

        pdf = pdfkit.from_string(render_to_string('down_pdf.html', {'books': books}), False, configuration=config)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="books.pdf"'
        return response

    elif 'Users' in request.POST:
        selected_users_ids = request.POST.getlist('selected_users')
        users = UsersBooks.objects.filter(id__in=selected_users_ids)
        selected_stors_ids = request.POST.getlist('selected_stors')
        storybook = StoryBook.objects.filter(id__in=selected_stors_ids)
        for user in users:
            user.story = storybook.filter(user = user.id)
        pdf = pdfkit.from_string(render_to_string('down_pdf.html', {'users': users}), False, configuration=config)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="users.pdf"'
        return response

    status_error = f'Произошла ошибка'
    return render(request, "page_search.html", {'status_error':status_error})


# процессы с пользователями
def processfunc(request):

    context = {}

    if 'delbookuser' in request.POST:
        user, book = map(int, request.POST.get('delbookuser').split())
        context['user'] = UsersBooks.objects.get(id=user)
        context['book'] = Book.objects.get(id=book)
        return render(request, 'book-user.html', context)

    elif 'Yes_book' in request.POST:
        user, book = map(int,request.POST.get('Yes_book').split())
        user_id = UsersBooks.objects.get(id=user)
        book = Book.objects.get(id=book)
        BookAndUser.objects.filter(user=user_id, book=book).delete()
        return redirect(f'/user/{user}')
    
    elif 'No_book' in request.POST:
        user = request.POST.get('No_book')
        return redirect(f'/user/{user}')

    elif 'addbookuser' in request.POST:
        user = request.POST.get('addbookuser')
        user = UsersBooks.objects.get(id=user)
        user_books = user.books.all()
        context['missing_books'] = Book.objects.exclude(id__in=user_books.values_list('id', flat=True))
        context['user'] = user
        return render(request, 'book-user.html', context)

    elif 'Addnewbookuser' in request.POST:
        selected_books_ids = request.POST.getlist('selected_books')
        user_id = request.POST.get('Addnewbookuser')
        user = UsersBooks.objects.get(id=user_id)
        books_ch = Book.objects.filter(id__in=selected_books_ids)
        for book in books_ch:
            BookAndUser.objects.create(user=user, book=book)
        return redirect(f'/user/{user_id}')

    return render(request, 'book-user.html')


# редактирование базы данных книги
def changebook(request):

    status = request.GET.get('status')

    if "Delete_book" in request.POST and request.POST.getlist('selected_books'):
        selected_books_ids = request.POST.getlist('selected_books')
        book = Book.objects.filter(id__in=selected_books_ids)
        return render(request, 'changebook.html', {'delform':book, 'status':'Проверте выбраные элементы перед удалением'})
    
    elif 'Del_books' in request.POST:
        selected_books_ids = request.POST.getlist('selected_books')
        for book_id in selected_books_ids:
            book = Book.objects.get(pk=book_id)
            book.delete()
        status = 'Данные удалены'
        return redirect(reverse('addbook') + f'?status={status}')

    elif 'Add_book' in request.POST:
        form = FormTableBook(request.POST)
        return render(request, 'changebook.html', {'form':form})

    elif 'Save_book' in request.POST:
        form = FormTableBook(request.POST)
        if form.is_valid():
            form.save()
            status = 'Книга добавлена'
            return redirect(reverse('addbook') + f'?status={status}')

    elif 'Change_books' in request.POST and request.POST.getlist('selected_books'):
        selected_books_ids = request.POST.getlist('selected_books')
        books_ch = Book.objects.filter(id__in=selected_books_ids)
        formset = BookFormSet(queryset=books_ch)
        return render(request,'changebook.html', {'formset':formset})
    
    elif 'Save_change_books' in request.POST:
        formset = BookFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            status = 'Данные изменены и сохранены'
            return redirect(reverse('addbook') + f'?status={status}')

    elif 'Change_books' in request.POST or "Delete_book" in request.POST:
        status = "Для начало выберите элемент(ы) которые хотите изменить либо удалить"
        
    form_book = Book.objects.all()
    return render(request,'changebook.html', {'form_book':form_book, 'status':status})


# редактирование базы данных пользователи
def changeuser(request):

    status = request.GET.get('status')

    if 'Add_user' in request.POST:
        form = FormTableUser(request.POST)
        return render(request, 'page_user.html', {'form':form})

    elif 'Save_user' in request.POST:
        form = FormTableUser(request.POST)
        if form.is_valid():
            form.save()
            status = 'Добавлен пользователь'
            return redirect(reverse('addusers') + f'?status={status}')

    elif "Delete_user" in request.POST and request.POST.getlist('selected_users'):
        selected_users_ids = request.POST.getlist('selected_users')
        user = UsersBooks.objects.filter(id__in=selected_users_ids)
        return render(request, 'page_user.html', {'delform':user, 'status':'Проверте выбраные элементы перед удалением'})
    
    elif 'Del_users' in request.POST:
        selected_users_ids = request.POST.getlist('selected_users')
        for user_id in selected_users_ids:
            user = UsersBooks.objects.get(pk=user_id)
            user.delete()
        status = 'Данные удалены'
        return redirect(reverse('addusers') + f'?status={status}')

    elif 'Change_users' in request.POST and request.POST.getlist('selected_users'):
        selected_users_ids = request.POST.getlist('selected_users')
        users_ch = UsersBooks.objects.filter(id__in=selected_users_ids)
        formset = UserFormSet(queryset=users_ch)
        return render(request,'page_user.html', {'formset':formset})
    
    elif 'Save_change_users' in request.POST:
        formset = UserFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            status = 'Данные изменены и сохранены'
            return redirect(reverse('addusers') + f'?status={status}')

    elif 'Change_users' in request.POST or "Delete_user" in request.POST:
        status = "Для начало выберите элемент(ы) которые хотите изменить либо удалить"

    form_user = UsersBooks.objects.all()
    return render(request, 'page_user.html', {'form_user':form_user, 'status':status})


# процесс получения книги(книг)
def funcissuance(request):
    status = request.GET.get('status')
    user = UsersBooks.objects.all()
    book = Book.objects.all()

    if "Add_books_user" in request.POST and request.POST.getlist('selected_books'):
        selected_books_ids = request.POST.getlist('selected_books')
        books_ch = Book.objects.filter(id__in=selected_books_ids)
        user_id = request.POST.get("Add_books_user")
        user = UsersBooks.objects.get(id=user_id)
        for book in books_ch:
            BookAndUser.objects.create(user=user, book=book)
        st = [book.name_book for book.name in books_ch]
        stbook = ', '.join(st)
        status = f'Пользователь - {user} получил книгу(книги):{stbook}'
        return redirect(reverse('issuance') + f'?status={status}') 

    elif "Add_books_user" in request.POST:
        user_id = request.POST.get("Add_books_user")
        user = UsersBooks.objects.get(id=user_id)
        status = f'Небыло выбранно ни одной книги для пользователя: {user}'
        return redirect(reverse('issuance') + f'?status={status}') 

    return render(request, 'issuance.html', {'user':user, 'book':book, 'status':status})


# процесс возврата книги(книг)
def funcunissuance(request):
    status = request.GET.get('status')
    user = UsersBooks.objects.all()
    book = Book.objects.all()

    if "Del_books_user" in request.POST and request.POST.getlist('selected_books'):
        selected_books_ids = request.POST.getlist('selected_books')
        books_ch = Book.objects.filter(id__in=selected_books_ids)
        user_id = request.POST.get("Del_books_user")
        user = UsersBooks.objects.get(id=user_id)
        for book in books_ch:
            BookAndUser.objects.filter(user=user, book=book).delete()
        st = [book.name_book for book.name in books_ch]
        stbook = ', '.join(st)
        status = f'Пользователь - {user} вернул книгу(книги):{stbook}'
        return redirect(reverse('issuance') + f'?status={status}') 

    elif "Del_books_user" in request.POST:
        user_id = request.POST.get("Del_books_user")
        user = UsersBooks.objects.get(id=user_id)
        status = f'Небыло выбранно ни одной книги для пользователя: {user}'
        return redirect(reverse('issuance') + f'?status={status}')

    return render(request, 'unissuance.html', {'user':user, 'book':book, 'status':status})


# дополнительная функция для фильтрации по базе данных
def filterfunc(ob, fil, text):
    id_ob = []
    text = text.upper()
    for k in ob:
        if fil == 'iexact' and k == text:
            id_ob.append(ob[k])
        elif fil == 'istartswith' and k.startswith(text):
            id_ob.append(ob[k])
        elif fil == 'iendswith' and k.endswith(text):
            id_ob.append(ob[k])
        elif fil == 'icontains' and text in k:
            id_ob.append(ob[k])
    return id_ob      