#!/usr/bin/env python3
"""Capture real browser evidence from the running app (pip install playwright)."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8080')
parser.add_argument('--chromium', default='/usr/bin/chromium')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
out = root / 'docs' / 'screenshots'
out.mkdir(parents=True, exist_ok=True)
observations = []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.chromium, headless=True,
                                args=['--no-sandbox', '--disable-dev-shm-usage'])
    context = browser.new_context(viewport={'width': 1200, 'height': 1000}, locale='en-US')
    page = context.new_page()

    def shot(name):
        page.screenshot(path=str(out / (name + '.png')), full_page=True)

    def form(title='Effective Java', author='Joshua Bloch', year='2018', genre='TECHNOLOGY', lang='en'):
        response = page.goto(args.base_url + '/books/new?lang=' + lang)
        assert response.status == 200
        page.locator('#title').fill(title)
        page.locator('#author').fill(author)
        page.locator('#year').fill(year)
        page.locator('#genre').select_option(genre)
        page.locator('input[type=checkbox][name=available]').check()
        with page.expect_navigation():
            page.locator('button[type=submit]').click()

    response = page.goto(args.base_url + '/')
    assert response.status == 200 and page.get_by_text('Open catalogue').is_visible()
    css = context.request.get(args.base_url + '/css/app.css')
    assert css.status == 200 and '.is-invalid' in css.text()
    page.goto(args.base_url + '/books?lang=en')
    assert page.locator('tbody tr').count() >= 3
    shot('01-catalogue')
    page.goto(args.base_url + '/books?author=Bloch')
    assert page.locator('tbody tr').count() == 1
    shot('02-filter')

    for name, kwargs, error in [
        ('03-empty-title', {'title': ''}, 'The title must not be empty'),
        ('04-year-range', {'year': '1200'}, 'The year must be between 1450 and 2100'),
        ('05-no-genre', {'genre': ''}, 'Choose a genre'),
        ('06-author-digits', {'author': 'Bloch 2018'}, 'The author must not contain digits'),
        ('07-russian-validation', {'title': '', 'lang': 'ru'}, 'Название не может быть пустым'),
        ('08-combined-errors', {'title': '', 'year': '1200', 'genre': ''}, 'The title must not be empty'),
    ]:
        before = len(context.request.get(args.base_url + '/api/books?limit=100').json())
        form(**kwargs)
        assert page.locator('.alert').is_visible()
        assert error in page.locator('.alert').inner_text()
        assert page.locator('#author').input_value() == kwargs.get('author', 'Joshua Bloch')
        assert len(context.request.get(args.base_url + '/api/books?limit=100').json()) == before
        shot(name)
        observations.append({'check': name, 'result': 'passed', 'error': error})

    before = len(context.request.get(args.base_url + '/api/books?limit=100').json())
    form(title='Spring MVC in Practice', author='Arzum Kassymzhanov', year='2026', genre='TECHNOLOGY')
    assert page.url.endswith('/books')
    assert 'Spring MVC in Practice' in page.locator('.flash').inner_text()
    shot('09-success-flash')
    page.reload()
    assert page.locator('.flash').count() == 0
    assert page.locator('tbody tr').count() == before + 1
    shot('10-refresh-no-duplicate')
    observations.append({'check': 'PRG and refresh', 'result': 'passed', 'before': before, 'after': before + 1})

    response = page.goto(args.base_url + '/books/999?lang=en')
    assert response.status == 404 and 'text/html' in response.headers['content-type']
    assert page.locator('h1').inner_text() == 'Book not found'
    shot('11-mvc-404')
    observations.append({'request': 'GET /books/999', 'status': response.status,
                         'contentType': response.headers['content-type'], 'handler': 'PageExceptionHandler'})

    for name, path, status in [
        ('12-api-404', '/api/books/999?lang=en', 404),
        ('13-search-valid', '/api/books/search?q=Java', 200),
        ('14-search-validation', '/api/books/search?q=a', 400),
        ('15-search-validation-ru', '/api/books/search?q=a&lang=ru', 400),
    ]:
        page.set_viewport_size({'width': 1200, 'height': 500})
        response = page.goto(args.base_url + path)
        assert response.status == status
        body = response.json()
        if status == 400:
            assert body['exception'] == 'HandlerMethodValidationException'
            assert body['errors'][0]['parameter'] == 'q'
        # Format only whitespace in the real response for readable evidence.
        page.locator('pre').evaluate('(element, body) => element.textContent = JSON.stringify(body, null, 2)', body)
        page.add_style_tag(content='body {margin: 28px; background: #f5f7fb;} pre {font: 18px/1.7 monospace; white-space: pre-wrap; overflow-wrap: anywhere; color: #15233b;}')
        shot(name)
        observations.append({'request': 'GET ' + path, 'status': status,
                             'contentType': response.headers['content-type'], 'body': body})

    for query, status in [('x', 400), ('xx', 200), ('x' * 60, 200), ('x' * 61, 400)]:
        response = context.request.get(args.base_url + '/api/books/search', params={'q': query, 'lang': 'en'})
        assert response.status == status
        observations.append({'check': 'search length ' + str(len(query)), 'status': response.status, 'result': 'passed'})
    missing = context.request.get(args.base_url + '/api/books/search')
    assert missing.status == 400

    for method, path, options, expected in [
        ('get', '/api/books/abc', {}, 400),
        ('get', '/api/nothing', {}, 404),
        ('delete', '/api/books', {}, 405),
        ('post', '/api/books', {'headers': {'Content-Type': 'text/plain'}, 'data': 'hello'}, 415),
        ('get', '/api/books', {'headers': {'Accept': 'application/xml'}}, 406),
    ]:
        response = getattr(context.request, method)(args.base_url + path, **options)
        assert response.status == expected
        observations.append({'request': method.upper() + ' ' + path, 'status': response.status, 'result': 'passed'})

    created = context.request.post(args.base_url + '/api/books', data={
        'title': 'API smoke book', 'author': 'Test Author', 'year': 2026})
    assert created.status == 201
    location = created.headers['location']
    observations.append({'request': 'POST /api/books', 'status': 201, 'location': location, 'body': created.json()})
    assert context.request.get(args.base_url + location).status == 200
    replaced = context.request.put(args.base_url + location, data={
        'title': 'Updated smoke book', 'author': 'Test Author', 'year': 2025})
    assert replaced.status == 200 and replaced.json()['title'] == 'Updated smoke book'
    assert context.request.delete(args.base_url + location).status == 204
    assert context.request.delete(args.base_url + location).status == 404
    observations.append({'check': 'REST create/read/replace/delete/delete-again', 'result': 'passed'})
    browser.close()

(root / 'docs' / 'browser-checks.json').write_text(json.dumps(observations, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'screenshots': len(list(out.glob('*.png'))), 'checks': len(observations), 'result': 'passed'}))
