#!/usr/bin/env python3
"""Generate the lab report from checked source code and captured evidence."""
import html
import json
import re
import subprocess
import functools
import http.server
import threading
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
docs = root / 'docs'
implementation = 'ec47757'
nodes = []

def heading(text, level=1): nodes.append(('heading', (level, text)))
def paragraph(text): nodes.append(('paragraph', text))
def table(headers, rows): nodes.append(('table', [headers] + rows))
def code(text, language='java'): nodes.append(('code', (language, text)))
def listing(title, path):
    heading(title, 2)
    paragraph(path)
    code((root / path).read_text(), 'html' if path.endswith('.html') else 'properties' if path.endswith('.properties') else 'java')
def screenshot(name, caption): nodes.append(('image', ('screenshots/' + name + '.png', caption)))

heading('1. Aim and project baseline')
paragraph('The aim of this work is to implement book form processing with Spring MVC and Thymeleaf: field binding, declarative validation, preservation of submitted values after errors, internationalization and centralized exception handling. The individual assignment is Variant 12: method validation of a search request parameter.')
paragraph('Student: Kassymzhanov Arzum. Group: IT1-2404IS. Course: RWPSF 3305 — Web Application Development with Spring Framework. Laboratory Work No. 6: Forms and validation.')
paragraph('Repository and branch: https://github.com/Karz317/spring-lab-01/tree/lab06')
paragraph('The baseline is branch lab04, commit bfaaf1278571960107ff2940e7cb27d4bb328b31. The available repository did not contain the catalogue from Laboratory Work No. 5, so Book, BookRepository, BookService, REST CRUD operations, catalogue pages, an author filter, CSS and a welcome page were added. The existing code from laboratory works 2–4 was preserved. Implementation commit for Laboratory Work No. 6: ' + implementation + '.')
table(['Component', 'Actual configuration'], [
    ['Java', 'JDK 25.0.4.1 LTS; archive SHA-256 verified'],
    ['Spring Boot', '4.1.1'], ['Maven', '3.9.16, repository wrapper'],
    ['Views', 'Thymeleaf; English and Russian resource bundles'],
    ['Validation', 'Jakarta Bean Validation, Hibernate Validator'],
    ['Storage', 'ConcurrentHashMap; three initial books; in-memory data'],
    ['Verification', '32 automated tests; 23 browser/HTTP check records'],
])

heading('2. Form object and validation rules')
paragraph('BookForm is separate from the immutable Book record. Getters and setters allow WebDataBinder to populate the object partially and redisplay it together with BindingResult. Users cannot bind an id through the form: @InitBinder allows only title, author, year, genre and available. Unlike the primitive int in the handout, the year uses Integer with @NotNull: an empty input receives the message “The year is required” rather than becoming 0.')
table(['Field', 'Constraint', 'Behavior'], [
    ['title', '@NotBlank, @Size(max=120)', 'An empty string, whitespace-only input and 121 characters are rejected'],
    ['author', '@NotBlank, @NoDigits', 'The name is required; digits, including Unicode digits, are forbidden'],
    ['year', '@NotNull, @Min(1450), @Max(2100)', '1450 and 2100 are accepted; empty and nonnumeric values are rejected'],
    ['genre', '@NotNull', 'A genre must be selected; an unknown enum value produces a binding error'],
    ['available', 'boolean', 'The checkbox value is persisted in Book'],
])
listing('Listing 1. BookForm', 'src/main/java/kz/iitu/springlab/web/BookForm.java')
listing('Listing 2. Genre', 'src/main/java/kz/iitu/springlab/web/Genre.java')
listing('Listing 3. Book', 'src/main/java/kz/iitu/springlab/catalog/Book.java')

heading('3. Controller and form template')
paragraph('GET /books/new adds a new BookForm and Genre.values() to the model. In the POST handler, BindingResult is placed immediately after @Valid @ModelAttribute("form"). If errors exist, genres is added back to the model and books/form is returned. A valid submission creates a book, adds a localized flash message and returns redirect:/books.')
paragraph('th:object selects the form object; *{title} refers to its property. th:field generates name, id and value, as well as selected or checked states for select and checkbox controls. th:errors displays messages, and th:errorclass highlights the field. The #fields error summary is inside the th:object scope so it can access BindingResult. novalidate makes the server-side validation visible during the demonstration.')
listing('Listing 4. BookPageController: GET, POST and PRG', 'src/main/java/kz/iitu/springlab/web/BookPageController.java')
listing('Listing 5. templates/books/form.html', 'src/main/resources/templates/books/form.html')

heading('4. Form checks and Post/Redirect/Get')
table(['Input / action', 'Observed result'], [
    ['Empty title; other fields completed', '200 HTML; title error; author, year, genre and checkbox preserved; no new book created'],
    ['Year 1200', '200 HTML; book.year.range beside the field and in the summary; 1200 remains in the input'],
    ['No genre selected', '200 HTML; book.genre.required; other values remain'],
    ['Author Bloch 2018', '200 HTML; the custom @NoDigits constraint rejects the value'],
    ['Empty title + year 1200 + no genre', 'All three errors appear together in the summary'],
    ['Valid form', 'POST /books → 302 Location: /books → GET /books → 200; a new book and flash message'],
    ['Page refresh', 'Another GET returns 200; the flash message disappears; the book count remains 4'],
])
for name, caption in [
    ('03-empty-title', 'Figure 1. An empty title is rejected; Joshua Bloch, 2018 and Technology are preserved.'),
    ('04-year-range', 'Figure 2. Year 1200 is rejected; the invalid value remains visible in the field.'),
    ('05-no-genre', 'Figure 3. A genre is required; the other submitted fields are preserved.'),
    ('09-success-flash', 'Figure 4. Successful POST: the redirect shows the new book and a flash message.'),
    ('10-refresh-no-duplicate', 'Figure 5. After refresh, the flash message is absent and the catalogue still contains four books.'),
    ('08-combined-errors', 'Figure 6. The error summary lists several violations simultaneously.'),
]: screenshot(name, caption)
paragraph('FlashMap stores the message between the POST and the following GET, normally through the HTTP session. The matching GET consumes it. Pressing F5 repeats the GET and does not invoke service.create again.')

heading('5. Interface and message internationalization')
paragraph('SessionLocaleResolver defaults to English and stores the selected locale in the session. LocaleChangeInterceptor reads lang. Labels, genre names, Bean Validation messages, type-conversion errors, flash messages and the 404 page use resource bundles. The mandatory messages.properties enables Spring Boot to configure MessageSource; messages_ru.properties contains the Russian translations. The following screenshots show the same title error in both languages. Russian text is retained in the localization screenshots and source bundle as evidence of the required second language.')
screenshot('03-empty-title', 'Figure 7. English labels and the validation message “The title must not be empty”.')
screenshot('07-russian-validation', 'Figure 8. Russian labels, genre name and validation message for the same empty-title error.')
listing('Listing 6. LocaleConfiguration', 'src/main/java/kz/iitu/springlab/config/LocaleConfiguration.java')
listing('Listing 7. messages.properties — complete default bundle', 'src/main/resources/messages.properties')
listing('Listing 8. messages_ru.properties — complete Russian bundle', 'src/main/resources/messages_ru.properties')

heading('6. Custom constraint @NoDigits')
paragraph('@NoDigits defines the mandatory message, groups and payload members, runtime retention and the link to NoDigitsValidator. A null value passes because @NotBlank handles a missing author. codePoints(), unlike chars(), also recognizes digits in supplementary Unicode planes. Tests cover ordinary digits, the Arabic digit ٢ and the mathematical digit 𝟙.')
listing('Listing 9. The @NoDigits annotation', 'src/main/java/kz/iitu/springlab/web/validation/NoDigits.java')
listing('Listing 10. NoDigitsValidator', 'src/main/java/kz/iitu/springlab/web/validation/NoDigitsValidator.java')
screenshot('06-author-digits', 'Figure 9. The custom constraint rejects the author value Bloch 2018.')

heading('7. Centralized exception handling')
paragraph('BookService throws BookNotFoundException when an identifier is missing. Each advice is scoped to a specific controller through assignableTypes. This avoids overlap between MVC and REST, since @RestController is also a @Controller. The page handler explicitly declares @ResponseStatus(NOT_FOUND); returning only a template name would otherwise produce status 200. The API returns an RFC 9457 ProblemDetail.')
table(['Request', 'Observed status / Content-Type', 'Handler'], [
    ['GET /books/999?lang=en', '404 · text/html;charset=UTF-8', 'PageExceptionHandler → error/not-found'],
    ['GET /api/books/999?lang=en', '404 · application/problem+json', 'ApiExceptionHandler → ProblemDetail'],
])
code(json.dumps(next(x['body'] for x in json.loads((docs/'browser-checks.json').read_text()) if x.get('request')=='GET /api/books/999?lang=en'), ensure_ascii=False, indent=2), 'json')
listing('Listing 11. BookNotFoundException', 'src/main/java/kz/iitu/springlab/catalog/BookNotFoundException.java')
listing('Listing 12. PageExceptionHandler', 'src/main/java/kz/iitu/springlab/web/PageExceptionHandler.java')
listing('Listing 13. ApiExceptionHandler', 'src/main/java/kz/iitu/springlab/web/ApiExceptionHandler.java')
screenshot('11-mvc-404', 'Figure 10. MVC returns the custom HTML 404 page.')
screenshot('12-api-404', 'Figure 11. REST returns the actual JSON ProblemDetail. Only JSON whitespace and indentation were formatted for readability.')

heading('8. Individual assignment — Variant 12')
paragraph('Assignment: place @Size directly on a @RequestParam of the search endpoint, demonstrate the resulting exception and handle it. The implementation provides GET /api/books/search?q=…. The query must contain 2–60 characters inclusive, and title matching is case-insensitive. A missing q defaults to an empty string and is rejected. A valid query without matching books returns 200 and [].')
paragraph('Spring MVC built-in method validation checks the parameter before invoking search and throws HandlerMethodValidationException when the constraint is violated. The controller has no class-level @Validated, which would select a different AOP validation path. The handler returns 400 application/problem+json with localized text, the actual exception name and errors identifying parameter q. The exception type is also written to the application log.')
listing('Listing 14. BookRestController, including the Variant 12 search endpoint', 'src/main/java/kz/iitu/springlab/web/BookRestController.java')
table(['Request / length', 'Result'], [
    ['q=Java', '200, Effective Java'], ['q=eFfEcTiVe', '200, case-insensitive matching'],
    ['Missing q / 0', '400 HandlerMethodValidationException'], ['q=a / 1', '400 HandlerMethodValidationException'],
    ['q=xx / 2', '200 []'], ['60 x characters', '200 []'], ['61 x characters', '400 HandlerMethodValidationException'],
    ['q=a&lang=ru', '400, Russian text in detail and errors'],
])
checks = json.loads((docs/'browser-checks.json').read_text())
code(json.dumps(next(x['body'] for x in checks if x.get('request')=='GET /api/books/search?q=a'), ensure_ascii=False, indent=2), 'json')
screenshot('13-search-valid', 'Figure 12. A valid q=Java request returns the matching book.')
screenshot('14-search-validation', 'Figure 13. q=a produces 400 and HandlerMethodValidationException in the handled response.')
screenshot('15-search-validation-ru', 'Figure 14. The same method validation error is localized into Russian.')

heading('9. Verification of the Laboratory Work No. 5 baseline')
paragraph('REST accepts a separate BookRequest. Genre and availability are optional in the original JSON request, so the commands from Laboratory Work No. 5 remain compatible. The repository assigns identifiers, PUT uses the id from the URL, and deleting an already deleted resource returns 404.')
table(['Operation', 'Verified result'], [
    ['GET /api/books?author=Bloch&limit=1', '200, JSON includes Joshua Bloch'],
    ['GET /api/books/{id}', '200 for an existing record; 404 ProblemDetail for a missing record'],
    ['POST /api/books', '201 + Location; the created resource can be read at Location'],
    ['PUT /api/books/{id}', '200 with the replaced record; 404 for a missing record'],
    ['DELETE /api/books/{id}', '204 with an empty body; a second DELETE returns 404'],
])
table(['Experiment', 'Status', 'Explanation'], [
    ['GET /api/books/abc', '400', 'abc cannot be converted to the long @PathVariable'],
    ['GET /api/nothing', '404', 'No matching route or static resource exists'],
    ['DELETE /api/books', '405', 'DELETE is not mapped to the collection path without an id'],
    ['POST /api/books, Content-Type: text/plain', '415', 'No suitable converter can read BookRequest from text/plain'],
    ['GET /api/books, Accept: application/xml', '406', 'The available converters cannot write the response in the requested representation'],
])
screenshot('01-catalogue', 'Figure 15. The styled catalogue with the three initial books.')
screenshot('02-filter', 'Figure 16. The author=Bloch filter leaves one matching record.')

heading('10. Automated verification and reproduction')
paragraph('bash mvnw -s /workspace/.tools/maven-settings.xml -B verify was executed with Java 25. It completed with BUILD SUCCESS and produced an executable JAR. After the fixes, the complete suite was rerun and the reusable cloud setup instructions were exercised separately. The server was started from the built JAR; browser checks used real headless Chromium through Playwright.')
table(['Suite', 'Executed', 'Failures / Errors / Skipped'], [
    ['BookWorkflowTests', '25', '0 / 0 / 0'], ['NoDigitsValidatorTests', '6', '0 / 0 / 0'],
    ['SpringLab01ApplicationTests', '1', '0 / 0 / 0'], ['Total', '32', '0 / 0 / 0'],
])
paragraph('The tests cover rejected submissions without insertion, year and query-length boundaries, invalid enum values, nonnumeric input, Russian locale persistence, one-time flash messages, persistence of genre/available, prevention of client-assigned identifiers, escaping of submitted HTML, REST CRUD and HTTP errors. Browser observations are stored in docs/browser-checks.json, and PNG captures are stored in docs/screenshots. These checks demonstrate the technical implementation; the student must still present and explain the application to the lecturer.')
code('bash mvnw clean verify\njava -jar target/spring-lab-01-0.0.1-SNAPSHOT.jar\n\n# In the prepared cloud environment:\nsource /workspace/.tools/java-env.sh\nbash mvnw -s /workspace/.tools/maven-settings.xml -B verify\n\n# Browser screenshots (Chromium and Playwright):\npython scripts/capture-evidence.py', 'bash')
paragraph('The demonstration uses the default profile on port 8080. The existing dev profile uses port 8081. No database or new secrets are required; in-memory data resets when the process restarts. Sending real email is not required for this assignment. Cloud Maven uses the supported proxy and existing system trust store with TLS verification enabled.')
paragraph('Windows working directory: C:\\Labworks\\Spring\\spring-lab-01-main. After obtaining the lab06 files and installing JDK 25, run the PowerShell commands below. Preserve the existing folder and local changes before replacing files. The complete Git project can also be cloned into a new adjacent directory, as documented in README.')
code("Set-Location 'C:\\Labworks\\Spring\\spring-lab-01-main'\n.\\mvnw.cmd clean verify\njava -jar .\\target\\spring-lab-01-0.0.1-SNAPSHOT.jar", 'powershell')

heading('11. Defence questions and answers')
answers = [
    ('Why is the form object separate from Book?', 'Input rules and mutable form state are separate from the domain record. The id is excluded from form binding to prevent mass assignment.'),
    ('What do th:object and *{title} mean?', 'th:object selects the form object from the model; *{title} refers to the title property of that object.'),
    ('What does th:field generate?', 'It generates name, id, value, selected/checked states and a hidden marker for checkboxes. On an error, it uses the rejected value from BindingResult.'),
    ('Why add an empty object in GET?', 'The template needs an object to evaluate th:field and to supply initial values before the first POST.'),
    ('What happens if @Valid is removed?', 'Binding and type conversion still occur, but the form constraints are not checked by Bean Validation.'),
    ('What if BindingResult is moved after Model?', 'It is no longer adjacent to the validated object, so Spring cannot associate it correctly. Invalid input may produce an exception instead of the normal error redisplay.'),
    ('Why add genres to the model again?', 'The available options are not submitted with POST or stored in BookForm; every rendering of the form must receive them.'),
    ('Where do form errors go?', 'BindingResult collects FieldError and ObjectError entries. The controller checks hasErrors; this differs from the method validation exception in Variant 12.'),
    ('How do NotNull, NotEmpty and NotBlank differ?', 'NotNull rejects null. NotEmpty also rejects an empty string or collection. NotBlank rejects a string that contains only whitespace.'),
    ('Where does an error message come from?', 'The key in message="{book.title.required}" is resolved by the validator through MessageSource and the active Locale. th:errors renders the resolved text.'),
    ('What is a field error versus a global error?', 'A field error belongs to one property; a global error belongs to the whole object, such as a class-level constraint. The constraints used in this form produce field errors.'),
    ('Why is messages.properties mandatory?', 'It is the default bundle needed for MessageSource auto-configuration and provides fallback text for missing translations.'),
    ('How is the language selected?', 'LocaleChangeInterceptor reads lang. SessionLocaleResolver stores the selection in the HTTP session. The default is English.'),
    ('What are the three mandatory constraint members?', 'message defines the text or bundle key; groups defines validation groups; payload provides additional violation metadata.'),
    ('Why does NoDigits accept null?', 'It checks for digits only. The separate NotBlank constraint enforces a required author.'),
    ('How are the advice classes scoped?', 'They use assignableTypes = BookPageController.class and BookRestController.class. Without scoping, an applicable handler could return the wrong representation.'),
    ('Which exception handler is selected?', 'Within an applicable controller or advice, the more specific matching exception type is preferred. Advice ordering also matters, and local controller handlers are checked before advice handlers.'),
    ('Why is th:utext unsafe for user input?', 'It inserts unescaped HTML and can enable XSS. This implementation uses th:text and the escaped values produced by th:field.'),
    ('Which exception is used in Variant 12?', 'Spring MVC built-in validation raises HandlerMethodValidationException. ApiExceptionHandler converts it to a 400 ProblemDetail with parameter q and a localized message.'),
]
for question, answer in answers:
    heading(question, 2); paragraph(answer)

heading('12. Conclusions')
paragraph('Declarative validation places input rules beside form properties and allows constraints to be reused without manual checks in controller methods. BindingResult associates violations with individual fields while preserving submitted values. Resource bundles separate text from code and switch the interface and validation messages together. Controller advice and method validation provide consistent HTML and REST error responses, while Post/Redirect/Get prevents duplicate creation when a page is refreshed.')
heading('13. References')
for text in [
    'Laboratory_work_6_EN.docx — primary assignment, Variant 12 and report requirements.',
    'Laboratory_work_5_EN.docx — REST and MVC catalogue prerequisites.',
    'Spring Framework: https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html',
    'Spring Boot: https://docs.spring.io/spring-boot/reference/features/internationalization.html',
    'Thymeleaf: https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html',
]: paragraph(text)

heading('Appendix. Repository and service')
listing('Listing 15. BookRepository', 'src/main/java/kz/iitu/springlab/catalog/BookRepository.java')
listing('Listing 16. BookService', 'src/main/java/kz/iitu/springlab/catalog/BookService.java')
listing('Listing 17. BookRequest — REST compatibility with Laboratory Work No. 5', 'src/main/java/kz/iitu/springlab/web/BookRequest.java')

# Render a title page and the same content to DOCX, Markdown and printable HTML.
doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Cm(21), Cm(29.7)
section.top_margin, section.bottom_margin = Cm(1.8), Cm(1.8)
section.left_margin, section.right_margin = Cm(2), Cm(2)
normal = doc.styles['Normal']; normal.font.name='Calibri'; normal.font.size=Pt(10)
normal.paragraph_format.space_after=Pt(7)
for name in ['Heading 1','Heading 2']:
    doc.styles[name].font.color.rgb=RGBColor.from_string('244B83')
code_style = doc.styles.add_style('Source Code', 1)
code_style.font.name='Consolas';code_style.font.size=Pt(8)
code_style.paragraph_format.space_after=Pt(0)
code_style.paragraph_format.line_spacing=1
footer = section.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('Kassymzhanov Arzum · IT1-2404IS · Lab 06   |   ')
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
for text, size in [
    ('JSC «International Information Technology University»',14),
    ('Faculty of Business, Media and Management\nDepartment of Information Systems',11),
    ('\n\nLABORATORY WORK No. 6',22),
    ('Forms and validation',18),
    ('Thymeleaf · Bean Validation · i18n\nController advice · Method validation',12),
    ('\nCourse: RWPSF 3305\nWeb Application Development with Spring Framework',12),
    ('\nPerformed by: Kassymzhanov Arzum\nGroup: IT1-2404IS\nVariant: 12 — Method validation',13),
    ('\n\nAlmaty, 2026',12),
]:
    par=doc.add_paragraph();par.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=par.add_run(text);run.font.size=Pt(size)
doc.add_page_break()
md=['# Laboratory Work No. 6 — Kassymzhanov Arzum\n\nIT1-2404IS · Variant 12\n']
parts=['<section class="cover"><h2>International Information Technology University</h2><p>Department of Information Systems</p><h1>LABORATORY WORK No. 6</h1><h2>Forms and validation</h2><p>RWPSF 3305 — Web Application Development with Spring Framework</p><p>Kassymzhanov Arzum<br>IT1-2404IS<br>Variant 12 — Method validation</p><p>Almaty, 2026</p></section>']
for kind, value in nodes:
    if kind=='heading':
        level,text=value;doc.add_heading(text,level=level)
        md.append('#'*(level+1)+' '+text+'\n');parts.append(f'<h{level+1}>{html.escape(text)}</h{level+1}>')
    elif kind=='paragraph':
        doc.add_paragraph(value);md.append(value+'\n');parts.append('<p>'+html.escape(value)+'</p>')
    elif kind=='code':
        lang,text=value
        for line in text.rstrip().splitlines():doc.add_paragraph(line,style='Source Code')
        doc.add_paragraph()
        md.append('```'+lang+'\n'+text.rstrip()+'\n```\n')
        parts.append('<pre><code>'+html.escape(text.rstrip())+'</code></pre>')
    elif kind=='table':
        t=doc.add_table(rows=1,cols=len(value[0]));t.style='Light Shading Accent 1'
        for i,s in enumerate(value[0]):t.rows[0].cells[i].text=s
        for row in value[1:]:
            cells=t.add_row().cells
            for i,s in enumerate(row):cells[i].text=s
        doc.add_paragraph()
        md.append('| '+' | '.join(value[0])+' |\n| '+' | '.join(['---']*len(value[0]))+' |\n'+'\n'.join('| '+' | '.join(r)+' |' for r in value[1:])+'\n')
        parts.append('<table>'+''.join('<tr>'+''.join(('<th>' if n==0 else '<td>')+html.escape(s)+('</th>' if n==0 else '</td>') for s in row)+'</tr>' for n,row in enumerate(value))+'</table>')
    elif kind=='image':
        path,caption=value
        par=doc.add_paragraph();par.alignment=WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next=True
        par.add_run().add_picture(str(docs/path),width=Inches(6.4))
        captionpar=doc.add_paragraph(caption);captionpar.alignment=WD_ALIGN_PARAGRAPH.CENTER
        captionpar.runs[0].italic=True;captionpar.runs[0].font.size=Pt(9)
        md.append(f'![{caption}]({path})\n\n{caption}\n')
        parts.append('<figure><img src="'+path+'"><figcaption>'+html.escape(caption)+'</figcaption></figure>')
doc.core_properties.author='Kassymzhanov Arzum'
doc.core_properties.title='Laboratory Work 6 — Forms and validation — Variant 12'
doc.save(docs/'Lab06_Kassymzhanov_Arzum.docx')
(docs/'report.md').write_text('\n'.join(md))
style='''@page {size:A4;margin:17mm 18mm;}body{font:11px/1.5 "DejaVu Sans",Arial;color:#16243b;}h1{font-size:25px;}h2{font-size:19px;color:#244b83;break-after:avoid;}h3{font-size:14px;color:#244b83;break-after:avoid;}p{overflow-wrap:anywhere;}pre{font:8px/1.4 "DejaVu Sans Mono",monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f9;border:1px solid #dce3ee;padding:10px;}table{border-collapse:collapse;width:100%;font-size:10px;margin:12px 0;}th,td{border:1px solid #dce3ee;padding:6px;text-align:left;}th{background:#eef3fa;}tr{break-inside:avoid;}figure{margin:18px 0;break-inside:avoid;text-align:center;}img{max-width:100%;max-height:205mm;object-fit:contain;}figcaption{font-size:10px;font-style:italic;margin-top:6px;}.cover{height:255mm;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;break-after:page;}.cover h1{margin-top:35px;}'''
(docs/'report.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Lab06 — Kassymzhanov Arzum</title><style>'+style+'</style></head><body>'+''.join(parts)+'</body></html>')
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(docs)))
threading.Thread(target=server.serve_forever, daemon=True).start()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/report.html');page.emulate_media(media='print')
    page.pdf(path=str(docs/'Lab06_Kassymzhanov_Arzum.pdf'),format='A4',print_background=True,
             display_header_footer=True,header_template='<span></span>',
             footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#667085">Kassymzhanov Arzum · IT1-2404IS · Lab 06 — <span class="pageNumber"></span> / <span class="totalPages"></span></div>')
    browser.close()
server.shutdown()
server.server_close()
print('DOCX, PDF, Markdown and HTML reports generated from verified source/evidence')
