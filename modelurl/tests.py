import doctest
from django.test import TestCase, Client

from modelurl import middleware, utils, macro
from example.models import Page, Item

class Test(TestCase):
    fixtures = ['example.json']
    
    def setUp(self):
        pass

    def test_middleware(self):
        doctest.testmod(middleware)
        
    def test_utils(self):
        doctest.testmod(utils)
        
    def test_threads(self):
        pass

    def tearDown(self):
        pass
