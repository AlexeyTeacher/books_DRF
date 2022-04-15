import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=100, author_name='Author 1')
        self.book_2 = Book.objects.create(name='Test book 2 ', price=1400, author_name='Author 2')
        self.book_3 = Book.objects.create(name='Test book 3', price=666, author_name='Author 1')
        self.book_4 = Book.objects.create(name='Author 1 Test book 3', price=100, author_name='Author 3')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book_1, self.book_2, self.book_3, self.book_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 100})
        serializer_data = BookSerializer([self.book_1, self.book_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': "Author 1"})
        serializer_data = BookSerializer([self.book_1, self.book_3, self.book_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': "price"})
        serializer_data = BookSerializer([self.book_1, self.book_4, self.book_3, self.book_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Programing in Python 3",
            "price": 809,
            "author_name": "Mark Summerfield"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(5, Book.objects.all().count())

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 1014,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(1014, self.book_1.price)

    def test_delete(self):
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(3, Book.objects.all().count())
