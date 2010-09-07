import os
from redsolutioncms.make import BaseMake
from redsolutioncms.models import CMSSettings
from modelurl.redsolution_setup.models import ModelUrlSettings

class Make(BaseMake):
    def make(self):
        super(Make, self).make()
        modelurl_settings = ModelUrlSettings.objects.get_settings()
        cms_settings = CMSSettings.objects.get_settings()
        cms_settings.render_to('settings.py', 'modelurl/redsolutioncms/settings.pyt', {
            'modelurl_settings': modelurl_settings,
        })

make = Make()

