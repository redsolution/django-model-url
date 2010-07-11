import os
from grandma.make import BaseMake
from grandma.models import GrandmaSettings
from modelurl.grandma_setup.models import ModelUrlSettings

class Make(BaseMake):
    def make(self):
        super(Make, self).make()
        modelurl_settings = ModelUrlSettings.objects.get_settings()
        grandma_settings = GrandmaSettings.objects.get_settings()
        grandma_settings.render_to('settings.py', 'modelurl/grandma/settings.py', {
            'modelurl_settings': modelurl_settings,
        })
