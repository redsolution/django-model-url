from django.db import models
from django.core.urlresolvers import reverse

class Page(models.Model):
    content = models.TextField()
    
    def get_absolute_url(self):
        return reverse('page_by_id', args=[self.id])

class Item(models.Model):
    barcode = models.CharField(max_length=100, unique=True)
    
    def my_url(self):
        return reverse('item_by_barcode', kwargs={'barcode': self.barcode})
