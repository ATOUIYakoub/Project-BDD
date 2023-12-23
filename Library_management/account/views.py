import datetime
from django.db import connection, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import User
from book import models as bModels
from .encrypt_util import *
from account.forms import AddBook, EditBook, EditUserProfileForm, UserLoginForm, UserRegistrationForm, ChangeUserPassForm, ProfileAvatarEdit, BookImage


def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def register(request):
    cursor = connection.cursor()
    page_number = 1
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cursor.execute('''INSERT INTO account_user
                       (username, email, password,image_file,is_admin,is_authenticated) VALUES (%s,%s,%s,%s,0,0)''', [cd['username'], cd['email'], encrypt(cd['password1']), 'uploads/images.png'])

            transaction.commit()
            messages.success(
                request, 'user registered successfully', 'success')

            return HttpResponseRedirect(reverse("book:home", args=[page_number]))
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login(request):
    cursor = connection.cursor()
    page_number = 1
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cursor.execute(
                'SELECT * FROM account_user WHERE email=%s', [cd['email']])
            try:
                user = dictfetchall(cursor)[0]
            except:
                user = None
            if user is not None and decrypt(user['password']) == cd['password']:
                cursor.execute(
                    'UPDATE account_user SET is_authenticated=1 WHERE id=%s', [user['id']])
                transaction.commit()
                messages.success(request, 'logged in successfully', 'success')
                return HttpResponseRedirect(reverse("book:home", args=[user['id'], page_number]))
            else:
                messages.error(
                    request, 'username or password is wrong', 'danger')
                return HttpResponseRedirect(reverse("account:login", args=[]))
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def logout(request, user_id):
    cursor = connection.cursor()
    page_number=1
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [user_id])
    user = dictfetchall(cursor)[0]
    cursor.execute(
        'UPDATE account_user SET is_authenticated=0 WHERE id=%s', [user['id']])
    transaction.commit()
    messages.success(request, 'logged out successfully', 'success')
    return HttpResponseRedirect(reverse("book:home", args=[page_number]))


def profile(request, id):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [id])
    user = dictfetchall(cursor)[0]
    cursor.execute(
        'SELECT * FROM book_bookinstance WHERE borrower_id=%s', [user['id']])
    users_books = dictfetchall(cursor)
    books_to_return = []
    for book in users_books:
        stime = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        if stime.date() == book['due_back'].date():
            books_to_return.append(book)
        elif datetime.datetime.utcnow().date() > book['due_back'].date():
            cursor.execute('SELECT * FROM book_book WHERE id=%s',
                           [book['book_id']])
            this_book = dictfetchall(cursor)[0]
            quantity_of_book = this_book['quantity']

            cursor.execute('DELETE FROM book_bookinstance WHERE id=%s AND borrower_id=%s', [
                           book['id'], user['id']])
            quantity_of_book += 1
            cursor.execute(
                'UPDATE book_book SET quantity=%s WHERE id=%s', [quantity_of_book, this_book['id']])
            transaction.commit()

    context = {
        'current_user': user,
        'books_to_return': books_to_return
    }

    return render(request, 'profile.html', context)


def info(request, id):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [id])
    current_user = dictfetchall(cursor)[0]

    cursor.execute(
        'SELECT * FROM book_bookinstance WHERE borrower_id=%s', [current_user['id']])
    users_books = dictfetchall(cursor)

    books = []

    for ub in users_books:
        cursor.execute('SELECT * FROM book_book WHERE id=%s',
                       [ub['book_id']])
        books.append(dictfetchall(cursor)[0])

    result = []

    for ub in users_books:
        for b in books:
            if (ub['book_id'] == b['id']):
                index = {'book_id': b['id'], 'title': b['title'],
                         'author': b['author'], 'due_back': ub['due_back']}
                result.append(index)

    context = {
        'current_user': current_user,
        'users_books': result,
    }

    return render(request, 'info.html', context)


def edit(request, id):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [id])
    user = dictfetchall(cursor)[0]
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cursor.execute(
                'UPDATE account_user SET email=%s,username=%s WHERE id=%s', [cd['email'], cd['username'], user['id']])
            transaction.commit()

            messages.success(
                request, 'User Edited Successfully', 'success')
            return HttpResponseRedirect(reverse("account:info", args=[user['id']]))

    else:
        form = EditUserProfileForm()
    return render(request, 'edit.html', {'form': form, 'current_user': user})


def change_avatar(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = ProfileAvatarEdit(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data.get("image_file")
            user.image_file = img
            user.save()
            return HttpResponseRedirect(reverse("account:info", args=[user.id]))
    else:
        form = ProfileAvatarEdit()
    return render(request, 'avatar.html', {'form': form, 'current_user': user})


def change_pass(request, id):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [id])
    user = dictfetchall(cursor)[0]

    if request.method == 'POST':
        form = ChangeUserPassForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if decrypt(user['password']) == cd['old_password']:
                cursor.execute(
                    'UPDATE account_user SET password=%s WHERE id=%s', [encrypt(cd['new_password']), user['id']])
                transaction.commit()
                messages.success(
                    request, 'Password Changed successfully.\nPlease Login Again.', 'success')
                return redirect('account:login')
            else:
                messages.error(
                    request, 'Old Password Does Not Match', 'danger')

    else:
        form = ChangeUserPassForm()
    return render(request, 'changepassword.html', {'form': form, "current_user": user})


def all_books(request, user_id, book_id=None):

    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [user_id])
    current_user = dictfetchall(cursor)[0]

    cursor.execute(
        'SELECT * FROM book_book')

    books = dictfetchall(cursor)

    cursor.execute('SELECT * FROM book_bookinstance')

    books_insts = dictfetchall(cursor)

    context = {
        'current_user': current_user,
        'books': books
    }
    if request.method == 'POST':
        for book_inst in books_insts:
            if book_inst['book_id'] == int(book_id):
                cursor.execute(
                    'DELETE FROM book_bookinstance WHERE book_id=%s', [book_id])
                transaction.commit()

        cursor.execute('DELETE FROM book_book WHERE id=%s', [book_id])
        transaction.commit()
        messages.success(request, 'The book deleted successfuly.', 'success')
        return HttpResponseRedirect(reverse("account:all_books", args=[user_id]))

    return render(request, 'book_list.html', context)


def all_users(request, user_id, del_id=None):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM account_user')
    users = dictfetchall(cursor)
    cursor.execute('SELECT * FROM account_user WHERE id=%s', [user_id])
    current_user = dictfetchall(cursor)[0]

    cursor.execute('SELECT * FROM book_bookinstance')
    books_insts = dictfetchall(cursor)

    context = {
        'current_user': current_user,
        'users': users
    }
    if request.method == 'POST':
        for book_inst in books_insts:
            if book_inst['borrower_id'] == int(del_id):
                cursor.execute(
                    'DELETE FROM book_bookinstance WHERE borrower_id=%s', [del_id])
                transaction.commit()
        cursor.execute('DELETE  FROM account_user WHERE id=%s', [del_id])
        transaction.commit()
        messages.success(request, 'The user deleted successfuly.', 'success')
        return HttpResponseRedirect(reverse("account:all_users", args=[user_id]))

    return render(request, 'user_list.html', context)


def add_user(request, user_id):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM account_user WHERE id=%s', [user_id])
    current_user = dictfetchall(cursor)[0]
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cursor.execute('''INSERT INTO account_user
                       (username, email, password,image_file,is_admin,is_authenticated) VALUES (%s,%s,%s,%s,0,0)''', [cd['username'], cd['email'], encrypt(cd['password1']), 'uploads/images.png'])

            transaction.commit()
            messages.success(
                request, 'user registered successfully', 'success')
            return HttpResponseRedirect(reverse("account:all_users", args=[user_id]))
    else:
        form = UserRegistrationForm()
    return render(request, 'add_user.html', {'form': form, 'current_user': current_user})


def add_book(request, user_id):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM account_user WHERE id=%s', [user_id])
    current_user = dictfetchall(cursor)[0]
    if request.method == 'POST':
        form = AddBook(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cursor.execute('''INSERT INTO book_book
                       (title, category_id, description,author,quantity,thumbnail) VALUES (%s,%s,%s,%s,%s,'')''', [cd['title'], cd['category'].id, cd['description'], cd['author'], cd['quantity']])
            transaction.commit()
            messages.success(request, 'Book added successfully', 'success')
            return HttpResponseRedirect(reverse("account:all_books", args=[user_id]))
    else:
        form = AddBook()
    return render(request, 'add_book.html', {'form': form, 'current_user': current_user})


def book_edit(request, user_id, book_id):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [user_id])
    current_user = dictfetchall(cursor)[0]

    cursor.execute('SELECT * FROM book_book WHERE id=%s', [book_id])
    book = dictfetchall(cursor)[0]

    cursor.execute(
        'SELECT * FROM book_bookinstance WHERE book_id=%s', [book_id])
    borowers = dictfetchall(cursor)
    result = []

    for ub in borowers:
        if (ub['book_id'] == book['id']):
            index = {
                'username': current_user['username'], 'email': current_user['email']}
            result.append(index)

    cursor.execute('SELECT * FROM book_category')
    categories = dictfetchall(cursor)

    bookORM = bModels.Book.objects.get(id=book_id)

    if request.method == 'POST':
        form = EditBook(request.POST)
        book_form = BookImage(request.POST, request.FILES)
        if form.is_valid() and book_form.is_valid():
            cd = form.cleaned_data
            img = book_form.cleaned_data.get("image_file")
            image = f'uploads/{img.name}'
            cursor.execute('UPDATE book_book SET title=%s,category_id=%s,description=%s,author=%s,quantity=%s,thumbnail=%s WHERE id=%s', [cd['title'], request.POST['category'],
                                                                                                                                          cd['description'], cd['author'], cd['quantity'], image, book_id])
            transaction.commit()
            messages.success(request, 'Book edited successfully', 'success')
            return HttpResponseRedirect(reverse("account:all_books", args=[user_id]))
    else:
        form = EditBook(instance=bookORM)
        book_form = BookImage()
    return render(request, 'book_edit.html', {'form': form, 'book_form': book_form, 'current_user': current_user, 'borrowers': result, 'categories': categories, 'book': book})


def add_category(request, user_id):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [user_id])
    current_user = dictfetchall(cursor)[0]

    if request.method == 'POST':
        name = request.POST['name']
        cursor.execute('''INSERT INTO book_category
                       (name) VALUES (%s)''', [name])
        transaction.commit()
        messages.success(request, 'Category added successfully', 'success')
        return HttpResponseRedirect(reverse("account:add_category", args=[user_id]))
    return render(request, 'add_category.html', {'current_user': current_user})


def change_avatar_(request, id):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM account_user WHERE id=%s', [id])
    user = dictfetchall(cursor)[0]
    if request.method == 'POST':
        form = ProfileAvatarEdit(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data.get("image_file")

            image = f'uploads/{img.name}'
            cursor.execute(
                'UPDATE account_user SET image_file=%s WHERE id=%s', [image, user['id']])
            transaction.commit()

            return HttpResponseRedirect(reverse("account:info", args=[user['id']]))
    else:
        form = ProfileAvatarEdit()
    return render(request, 'avatar.html', {'form': form, 'current_user': user})
