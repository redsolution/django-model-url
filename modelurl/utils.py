from pages.models import Page, Content
import re

def get_changes_for_pages():
    changes = []
    for page in Page.objects.all():
        url = page.get_absolute_url()
        if not url:
            continue
        if len(url) > 1 and url[-1] == '/':
            url = url[:-1]
        url = re.escape(url)
        repl = '{%% model_url \'pages.model.Page\' %d %%}' % page.id
        changes.append((re.compile('"%s/?"' % url), '"%s"' % repl))
        changes.append((re.compile('"%s/?#' % url), '"%s#' % repl))
    return changes


def apply_changes(body, changes):
    for pattern, repl in changes:
        body = re.sub(pattern, repl, body)
    return body


def process_pages(log=False, changes=None):
    if changes is None:
        changes = get_changes_for_pages()
    if log:
        old = open('modelurl.old', 'w')
        new = open('modelurl.new', 'w')
    for content in Content.objects.all():
        if Content.objects.filter(
            language=content.language, type=content.type, page=content.page).latest() != content:
            continue
        body = apply_changes(content.body, changes)
        if log:
            if body != content.body:
                old.write('\n------%d----\n' % content.page.id)
                old.write(content.body.encode('utf8'))
                new.write('\n------%d----\n' % content.page.id)
                new.write(body.encode('utf8'))
        Content.objects.create_content_if_changed(
            content.page, content.language, content.type, body)
    if log: 
        old.close()
        new.close()
