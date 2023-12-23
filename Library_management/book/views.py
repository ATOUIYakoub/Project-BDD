import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from account import models as accountModels
from django.db import connection, transaction
from . import models
from django.core.paginator import Paginator


def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def home(request, id=None, page_number=1):

    cursor = connection.cursor()

    cursor.execute('SELECT * FROM book_book')

    books = Paginator(dictfetchall(cursor), 6)

    cursor.execute('SELECT * FROM book_category')

    categories = dictfetchall(cursor)

    prev_num = int(page_number)-1
    next_num = int(page_number)+1

    if id:
        cursor.execute('SELECT * FROM account_user WHERE id=%s', [id])

        current_user = dictfetchall(cursor)[0]

        context = {
            'books': books.page(page_number).object_list,
            'current_user': current_user,
            'categories': categories,
            'page_number': page_number,
            'prev_num': prev_num,
            'next_num': next_num


        }
    else:
        context = {
            'books': books.page(page_number).object_list,
            'categories': categories,
            'page_number': page_number,
            'prev_num': prev_num,
            'next_num': next_num

        }

    return render(request, 'home.html', context=context)


def single(request, book_id, user_id=None):

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM book_book WHERE id=%s', [book_id])

    book = dictfetchall(cursor)[0]
    cursor.execute(
        'select name from book_category where id=%s', [book['category_id']])

    categ_name = dictfetchall(cursor)[0]

    if user_id:

        cursor.execute('SELECT * FROM account_user WHERE id=%s', [user_id])

        current_user = dictfetchall(cursor)[0]

        cursor.execute(
            'SELECT * FROM book_bookinstance WHERE book_id=%s AND borrower_id=%s', [book_id, user_id])

        book_inst = dictfetchall(cursor)

        context = {
            'book': book,
            'current_user': current_user,
            'book_inst': book_inst,
            'categ_name': categ_name
        }
    else:
        context = {
            'book': book,
            'categ_name': categ_name
        }

    return render(request, 'singel.html', context)


def borrow(request, book_id, user_id=None):
    cursor = connection.cursor()

    if user_id:
        if request.method == "POST":
            cursor.execute('SELECT * FROM book_book WHERE id=%s', [book_id])
            this_book = dictfetchall(cursor)[0]

            cursor.execute('SELECT * FROM account_user WHERE id=%s', [user_id])
            current_user = dictfetchall(cursor)[0]

            if this_book['quantity'] != 0:
                quantity_of_book = this_book['quantity']
                due_back = datetime.datetime.utcnow() + datetime.timedelta(days=15)
                cursor.execute('''INSERT INTO book_bookinstance
                       (book_id, borrower_id,due_back,loan_status) VALUES (%s,%s,%s,1)''', [this_book['id'], current_user['id'], due_back])

                quantity_of_book -= 1

                cursor.execute(
                    'UPDATE book_book SET quantity=%s WHERE id=%s', [quantity_of_book, book_id])

                transaction.commit()

                return HttpResponseRedirect(reverse("book:single", kwargs={'user_id': user_id, 'book_id': book_id}))

        else:
            return HttpResponseRedirect(reverse("book:single", kwargs={'user_id': user_id, 'book_id': book_id}))

    else:
        return redirect('account:login')


def return_back(request, book_id, user_id):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM book_book WHERE id=%s', [book_id])
    book = dictfetchall(cursor)[0]

    cursor.execute('SELECT * FROM account_user WHERE id=%s', [user_id])
    current_user = dictfetchall(cursor)[0]

    if request.method == "POST":

        quantity_of_book = book['quantity']
        cursor.execute('DELETE FROM book_bookinstance WHERE book_id=%s AND borrower_id=%s', [
            book['id'], current_user['id']])

        quantity_of_book += 1
        cursor.execute(
            'UPDATE book_book SET quantity=%s WHERE id=%s', [quantity_of_book, book['id']])
        transaction.commit()

        return HttpResponseRedirect(reverse("book:single", kwargs={'user_id': user_id, 'book_id': book_id}))

    else:
        return HttpResponseRedirect(reverse("book:single", kwargs={'user_id': user_id, 'book_id': book_id}))


def search(request, id=None, page_number=1):

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM book_book')

    list_books = []
    search_input = request.GET['s']
    books = dictfetchall(cursor)
    for book in books:
        if len(search_input) > 0:
            if search_input.lower() in book['title'].lower() or search_input.lower() in book['description'].lower() or search_input.lower() in book['author'].lower():
                list_books.append(book)

    temp_book = Paginator(list_books, 6)

    prev_num = int(page_number)-1
    next_num = int(page_number)+1

    if id:
        cursor.execute('SELECT * FROM account_user WHERE id=%s', [id])
        current_user = dictfetchall(cursor)[0]
        context = {
            'search_input': search_input,
            'current_user': current_user,
            'books': temp_book.page(page_number).object_list,
            'page_number': page_number,
            'prev_num': prev_num,
            'next_num': next_num
        }
    else:
        context = {
            'search_input': search_input,
            'books': temp_book.page(page_number).object_list,
            'page_number': page_number,
            'prev_num': prev_num,
            'next_num': next_num
        }
    return render(request, 'search.html', context)


def categories(request, name, id=None, page_number=1):

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM book_category where name=%s', [name])

    categ = dictfetchall(cursor)[0]

    cursor.execute(
        'SELECT * FROM book_book where category_id=%s', [categ['id']])

    books = Paginator(dictfetchall(cursor), 6)

    prev_num = int(page_number)-1
    next_num = int(page_number)+1
    if id:
        cursor.execute('SELECT * FROM account_user WHERE id=%s', [id])
        current_user = dictfetchall(cursor)[0]
        context = {
            'current_user': current_user,
            'books': books.page(page_number).object_list,
            'name': name,
            'page_number': page_number,
            'prev_num': prev_num,
            'next_num': next_num

        }
    else:
        context = {
            'books': books.page(page_number).object_list,
            'name': name,
            'page_number': page_number,
            'prev_num': prev_num,
            'next_num': next_num

        }

    return render(request, 'categories.html', context)
