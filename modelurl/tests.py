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
        
    def test_marco(self):
        client = Client()
        page = Page.objects.get(pk=1)
        self.assertEqual(client.get('/page_by_id/1').content, 'page')

        item = Item.objects.get(pk=1)
        self.assertEqual(item.my_url(), '/item_by_barcode/first')
        
        value = macro(item)
        self.assertEqual(value, '{@ example.models.Item 1 @}')
        
        page.content = '<a href="%s">1</a>' % value
        page.save()
        self.assertEqual(client.get('/page_by_id/1').content, '<a href="/item_by_barcode/first">1</a>')
        
        item.barcode = 'changed'
        item.save()
        self.assertEqual(client.get('/page_by_id/1').content, '<a href="/item_by_barcode/changed">1</a>')

        page.content = '<a href="{@ example.models.DoesNotExists 1 @}">1</a>'
        page.save()
        self.assertEqual(client.get('/page_by_id/1').content, '<a href="">1</a>')

        page.content = '<a href="{@ example.models.Page 1 @}">1</a>'
        page.save()
        self.assertEqual(client.get('/page_by_id/1').content, '<a href="/page_by_id/1">1</a>')
        
#    def test_dict(self):
#    >>> replace = ReplaceByDict(urls)
#    >>> replace.url('/about')
#    '{@ pages.model.Page 7 @}'
#    >>> replace.text('<a href="/about">about</a>')
#    '<a href="{@ pages.model.Page 7 @}">about</a>'
        

    def tearDown(self):
        pass
