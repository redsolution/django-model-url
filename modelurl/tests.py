import doctest
from django.test import TestCase

class Test(TestCase):
    fixtures = ['example.json']

    def setUp(self):
        pass

    def test_middleware(self):
        import middleware
        doctest.testmod(middleware)

    def test_utils(self):
        import utils
        doctest.testmod(utils)

    def test_threads(self):
        pass

    def tearDown(self):
        pass
