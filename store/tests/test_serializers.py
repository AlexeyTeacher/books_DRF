from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user_1 = User.objects.create(username='test_username 1',
                                     first_name='Alexey', last_name='Kokorin')
        user_2 = User.objects.create(username='test_username 2',
                                     first_name='Gleb', last_name='Ivanov')
        user_3 = User.objects.create(username='test_username 3',
                                     first_name='Irina', last_name='Petrova')

        book_1 = Book.objects.create(name='Test book 1', price=100, author_name='Author 1', owner=user_1)
        book_2 = Book.objects.create(name='Test book 2', price=1400, author_name='Author 2')

        UserBookRelation.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user_2, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user_3, book=book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=user_1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user_2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user_3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')

        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '100.00',
                'author_name': 'Author 1',
                'annotated_likes': 3,
                'rating': '4.67',
                'owner_name': 'test_username 1',
                'readers': [
                    {
                        'first_name': 'Alexey',
                        'last_name': 'Kokorin'
                    },
                    {
                        'first_name': 'Gleb',
                        'last_name': 'Ivanov'
                    },
                    {
                        'first_name': 'Irina',
                        'last_name': 'Petrova'
                    }
                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '1400.00',
                'author_name': 'Author 2',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': '',
                'readers': [
                    {
                        'first_name': 'Alexey',
                        'last_name': 'Kokorin'
                    },
                    {
                        'first_name': 'Gleb',
                        'last_name': 'Ivanov'
                    },
                    {
                        'first_name': 'Irina',
                        'last_name': 'Petrova'
                    }
                ]
            }
        ]
        self.assertEqual(expected_data, data)