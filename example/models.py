from django.db import models
from django.core.urlresolvers import reverse

class Page(models.Model):
    content = models.TextField()
    
    def get_absolute_url(self):
        return reverse('page', args=[self.id])

class Item(models.Model):
    barcode = models.CharField(max_length=100, unique=True)
    
    def my_url(self):
        return reverse('item', kwargs={'barcode': self.barcode})
