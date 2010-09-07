from django.contrib import admin
from modelurl.redsolution_setup.models import ModelUrlSettings, ModelUrlModel, ModelUrlView

class ModelUrlModelInline(admin.TabularInline):
    model = ModelUrlModel

class ModelUrlViewInline(admin.TabularInline):
    model = ModelUrlView

class ModelUrlForm(admin.ModelAdmin):
    model = ModelUrlSettings
    inlines = [ModelUrlModelInline, ModelUrlViewInline]

try:
    admin.site.register(ModelUrlSettings, ModelUrlForm)
except admin.sites.AlreadyRegistered:
    pass
