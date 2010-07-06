from django.http import *
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse

from models import Page, Item

def response(request):
    return HttpResponse('Done')

def notfound(request):
    return HttpResponseNotFound('Not found')

def error(request):
    return HttpResponseServerError('Error')

def redirect_response(request):
    return HttpResponseRedirect(reverse('response'))

def redirect_notfound(request):
    return HttpResponseRedirect(reverse('notfound'))

def redirect_redirect_response(request):
    return HttpResponseRedirect(reverse('redirect_response'))

def redirect_cicle(request):
    return HttpResponseRedirect(reverse('redirect_cicle'))

def redirect_a_to_redirect_b_cicle(request):
    return HttpResponseRedirect(reverse('redirect_b_to_redirect_a_cicle'))

def redirect_b_to_redirect_a_cicle(request):
    return HttpResponseRedirect(reverse('redirect_a_to_redirect_b_cicle'))

def redirect_page1(request):
    return HttpResponseRedirect(reverse('page_by_id', args=['1']))

def redirect_page12(request):
    return HttpResponseRedirect(reverse('page_by_id', args=['12']))

def permanent_redirect_response(request):
    return HttpResponsePermanentRedirect(reverse('response'))

def http404(request):
    raise Http404

def http500(request):
    raise Exception

def request_true_response(request):
    from urlmethods import local_check
    result = local_check(reverse('response'))
    if result:
        return HttpResponse('True')
    else:
        return HttpResponse('False')

def request_false_response(request):
    from urlmethods import local_check
    result = local_check(reverse('notfound'))
    if result:
        return HttpResponse('True')
    else:
        return HttpResponse('False')

def page_by_id(request, pk):
    page = get_object_or_404(Page, pk=pk)
    return render_to_response('page.html', locals())

def item_by_id(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render_to_response('item.html', locals())

def item_by_barcode(request, barcode):
    item = get_object_or_404(Item, barcode=barcode)
    return render_to_response('item.html', locals())
