# Updates the GoalKicker Books

'''
Get the names of the GoalKicker books you need to update, using the books in the current dir.
For each book, 
    get it's 'creation date', I.e. the date it was last updated.
    build it's url, and get the last time the book was updated in GoalKicker
    If the date Goalkicker udpated the book is more recent than the books' creation date,
        delete the existing book
        redownload the book from goalkicker.

'''

import os
import datetime
import requests
from lxml import html
import re
import time

BOOK_IDENTIFIER = 'NotesForProfessionals.pdf'

# METHODS
def gather_books_to_update():

    print('Gathering books to update...')

    books_to_update = {}

    with os.scandir() as dir_entries:

        for entry in dir_entries:

            file_name = entry.name

            if BOOK_IDENTIFIER in file_name:

                file_stats = entry.stat()

                file_creation_date_in_sec = file_stats.st_mtime

                file_creation_date = datetime.datetime.fromtimestamp(file_creation_date_in_sec)

                books_to_update[file_name] = file_creation_date

    print('...gathered {} books to update.'.format(len(books_to_update)))

    return books_to_update

def get_book_url(book):

    return 'https://books.goalkicker.com/' + book.replace(BOOK_IDENTIFIER,'Book')

def gather_date_book_last_updated(book):

    book_url = get_book_url(book)

    url_response = requests.get(book_url)

    book_html = html.fromstring(url_response.content)

    date_container = book_html.xpath("//div[@class='notice']/p/text()")[4]

    date_string = re.match(r'.+? pages, published on (.+)',date_container).group(1)

    update_date = datetime.datetime.strptime(date_string,'%B %Y')

    return update_date

def update_book(book):

    os.remove(book)

    download_url = get_book_url(book) + '/' + book

    book_content = requests.get(download_url)

    with open(book,'wb+') as out_file:

        out_file.write(book_content.content)


# EXECUTION

def main():

    books_to_update = gather_books_to_update()

    books_updated = []

    print('Updating books...')

    for book in books_to_update.keys():

        creation_date = books_to_update[book]

        last_updated = gather_date_book_last_updated(book)

        if (last_updated.year > creation_date.year
        or last_updated.month > creation_date.month): 
        
            update_book(book)

            books_updated.append(book)

        time.sleep(2) # Sleep for a couple seconds so you don't upset the website's host server.

    print('...Done.')

    print('Updated {} books{}'.format(len(books_updated), (
        '.' if len(books_updated) == 0 else ':\n' +'\n'.join(books_updated)
    )))