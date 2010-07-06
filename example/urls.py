from django.conf.urls.defaults import *

urlpatterns = patterns('')

for view in ['response', 'notfound', 'error', 'redirect_response',
    'redirect_notfound', 'redirect_redirect_response', 'redirect_cicle',
    'redirect_a_to_redirect_b_cicle', 'redirect_b_to_redirect_a_cicle',
    'redirect_page1', 'redirect_page12', 'permanent_redirect_response',
    'http404', 'http500', 'request_true_response', 'request_false_response', ]:
    urlpatterns += patterns('example.views', url(r'^%s$' % view, view, name=view))

urlpatterns += patterns('example.views',
    url(r'^page_by_id/(\d{1,8})$', 'page_by_id', name='page_by_id'),
    url(r'^item_by_id/(\d{1,8})$', 'item_by_id', name='item_by_id'),
    url(r'^item_by_barcode/(?P<barcode>\w+)$', 'item_by_barcode', name='item_by_barcode'),
)
