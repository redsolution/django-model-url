from django.test import TestCase, Client
from models import Page, Item

class Test(TestCase):
    fixtures = ['example.json']

    def setUp(self):
        pass

    def test_objects(self):
        page = Page.objects.get(pk=1)
        item = Item.objects.get(pk=1)
        self.assertEqual(page.get_absolute_url(), '/page_by_id/1')
        self.assertEqual(item.my_url(), '/item_by_barcode/first')
        self.assertEqual(Page.objects.get(pk=1).content, 'page')
        self.assertEqual(Page.objects.get(pk=11).content, 'eleven')
        self.assertEqual(Item.objects.get(pk=1).barcode, 'first')
        self.assertEqual(Item.objects.get(pk=2).barcode, 'second')

    def test_views(self):
        client = Client()
        self.assertEqual(client.get('/response').status_code, 200)
        self.assertEqual(client.get('/notfound').status_code, 404)
        self.assertEqual(client.get('/error').status_code, 500)
        self.assertEqual(client.get('/redirect_response').status_code, 302)
        self.assertEqual(client.get('/redirect_notfound').status_code, 302)
        self.assertEqual(client.get('/redirect_redirect_response').status_code, 302)
        self.assertEqual(client.get('/redirect_a_to_redirect_b_cicle').status_code, 302)
        self.assertEqual(client.get('/redirect_b_to_redirect_a_cicle').status_code, 302)
        self.assertEqual(client.get('/redirect_page1').status_code, 302)
        self.assertEqual(client.get('/redirect_page12').status_code, 302)
        self.assertEqual(client.get('/redirect_cicle').status_code, 302)
        self.assertEqual(client.get('/permanent_redirect_response').status_code, 301)
        self.assertEqual(client.get('/http404').status_code, 404)
        self.assertRaises(Exception, client.get, '/http500')
        self.assertEqual(client.get('/request_true_response').content , 'True')
        self.assertEqual(client.get('/request_false_response').content , 'False')
        self.assertEqual(client.get('/doesnotexists').status_code, 404)
        self.assertEqual(client.get('/page_by_id/1').content, 'page')
        self.assertEqual(client.get('/page_by_id/2').status_code, 404)
        self.assertEqual(client.get('/page_by_id/11').content, 'eleven')
        self.assertEqual(client.get('/page_by_id/string').status_code, 404)
        self.assertEqual(client.get('/item_by_id/1').content, 'first')
        self.assertEqual(client.get('/item_by_id/2').content, 'second')
        self.assertEqual(client.get('/item_by_id/3').status_code, 404)
        self.assertEqual(client.get('/item_by_id/string').status_code, 404)
        self.assertEqual(client.get('/item_by_barcode/first').content, 'first')
        self.assertEqual(client.get('/item_by_barcode/second').content, 'second')
        self.assertEqual(client.get('/item_by_barcode/string').status_code, 404)

    def tearDown(self):
        pass
