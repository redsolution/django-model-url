# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from redsolutioncms.models import BaseSettings

class ModelUrlSettings(BaseSettings):
    pass

class ModelUrlModel(models.Model):
    settings = models.ForeignKey(ModelUrlSettings, related_name='models')
    model = models.CharField(verbose_name=_('Mode'), max_length=255)

class ModelUrlView(models.Model):
    settings = models.ForeignKey(ModelUrlSettings, related_name='views')
    view = models.CharField(verbose_name=_('View'), max_length=255)
    object = models.CharField(verbose_name=_('Object'), max_length=255)
