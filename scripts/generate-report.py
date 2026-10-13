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

heading('1. Цель и исходный проект')
paragraph('Цель работы — реализовать обработку формы книги средствами Spring MVC и Thymeleaf: связывание полей, декларативную валидацию, сохранение введённых значений при ошибках, локализацию и централизованную обработку исключений. Индивидуальное задание — вариант 12: method validation параметра поискового запроса.')
paragraph('Студент: Kassymzhanov Arzum. Группа: IT1-2404IS. Курс: RWPSF 3305 — Web Application Development with Spring Framework. Лабораторная работа №6: Forms and validation.')
paragraph('Репозиторий и ветка: https://github.com/Karz317/spring-lab-01/tree/lab06')
paragraph('Исходная ветка lab04, коммит bfaaf1278571960107ff2940e7cb27d4bb328b31. В доступном репозитории отсутствовала основа лабораторной №5, поэтому добавлены Book, BookRepository, BookService, REST CRUD, страницы каталога, фильтр, CSS и стартовая страница. Существующий код лабораторных №2–4 сохранён. Коммит реализации №6: ' + implementation + '.')
table(['Компонент', 'Фактически использовано'], [
    ['Java', 'JDK 25.0.4.1 LTS; SHA-256 архива проверен'],
    ['Spring Boot', '4.1.1'], ['Maven', '3.9.16, repository wrapper'],
    ['Представления', 'Thymeleaf; английский и русский resource bundles'],
    ['Валидация', 'Jakarta Bean Validation, Hibernate Validator'],
    ['Хранилище', 'ConcurrentHashMap; три начальные книги; данные в памяти'],
    ['Проверки', '32 автоматических теста; 23 записи браузерных/HTTP-проверок'],
])

heading('2. Модель формы и правила валидации')
paragraph('BookForm отделён от неизменяемого record Book. Getters и setters позволяют WebDataBinder заполнить объект частично и вернуть его в форму вместе с BindingResult. Пользователь не может связать форму с id: @InitBinder разрешает только title, author, year, genre и available. В отличие от примера методички, год представлен Integer с @NotNull: пустое поле получает понятное сообщение «Укажите год», а не превращается в 0.')
table(['Поле', 'Ограничение', 'Поведение'], [
    ['title', '@NotBlank, @Size(max=120)', 'Пустая строка, пробелы и 121 символ отклоняются'],
    ['author', '@NotBlank, @NoDigits', 'Имя обязательно; цифры, включая Unicode, запрещены'],
    ['year', '@NotNull, @Min(1450), @Max(2100)', 'Границы 1450 и 2100 допустимы; пустое и нечисловое значение отклоняются'],
    ['genre', '@NotNull', 'Выбор жанра обязателен; неизвестное значение даёт ошибку связывания'],
    ['available', 'boolean', 'Значение checkbox сохраняется в Book'],
])
listing('Листинг 1. BookForm', 'src/main/java/kz/iitu/springlab/web/BookForm.java')
listing('Листинг 2. Genre', 'src/main/java/kz/iitu/springlab/web/Genre.java')
listing('Листинг 3. Book', 'src/main/java/kz/iitu/springlab/catalog/Book.java')

heading('3. Контроллер и шаблон формы')
paragraph('GET /books/new помещает в модель новый BookForm и Genre.values(). В POST параметр BindingResult расположен непосредственно после @Valid @ModelAttribute("form"). Если имеются ошибки, genres снова добавляется в модель и возвращается books/form. При успехе создаётся книга, локализованное сообщение передаётся через flash и выполняется redirect:/books.')
paragraph('th:object задаёт объект формы; *{title} обращается к его свойству. th:field генерирует name, id и value, а для select и checkbox — выбранное состояние. th:errors показывает сообщения; th:errorclass выделяет поле. Блок #fields размещён внутри области th:object, чтобы summary имел доступ к BindingResult. novalidate позволяет продемонстрировать именно серверную проверку.')
listing('Листинг 4. BookPageController: GET, POST, PRG', 'src/main/java/kz/iitu/springlab/web/BookPageController.java')
listing('Листинг 5. templates/books/form.html', 'src/main/resources/templates/books/form.html')

heading('4. Проверка формы и Post/Redirect/Get')
table(['Ввод / действие', 'Результат'], [
    ['Пустое название; остальные поля заполнены', '200 HTML; ошибка title; автор, год, жанр и checkbox сохранены; новая книга не создана'],
    ['Год 1200', '200 HTML; book.year.range рядом с полем и в summary; введённый 1200 остаётся'],
    ['Жанр не выбран', '200 HTML; book.genre.required; остальные значения остаются'],
    ['Автор Bloch 2018', '200 HTML; срабатывает собственный @NoDigits'],
    ['Пустое название + 1200 + без жанра', 'Все три ошибки одновременно перечислены в summary'],
    ['Корректная форма', 'POST /books → 302 Location: /books → GET /books → 200; новая книга и flash'],
    ['Обновление страницы', 'Повторный GET 200; flash исчез; число книг осталось 4'],
])
for name, caption in [
    ('03-empty-title', 'Рисунок 1. Пустое название отклонено; Joshua Bloch, 2018 и Technology сохранены.'),
    ('04-year-range', 'Рисунок 2. Год 1200 отклонён; неверное значение остаётся в поле.'),
    ('05-no-genre', 'Рисунок 3. Жанр обязателен; остальные поля не потеряны.'),
    ('09-success-flash', 'Рисунок 4. Успешный POST: после перенаправления появилась новая книга и flash.'),
    ('10-refresh-no-duplicate', 'Рисунок 5. После обновления flash отсутствует; в каталоге остаются четыре книги.'),
    ('08-combined-errors', 'Рисунок 6. Summary показывает несколько ошибок одновременно.'),
]: screenshot(name, caption)
paragraph('FlashMap хранит сообщение между POST и последующим GET, обычно с использованием HTTP-сессии. После совпавшего GET оно потребляется. F5 повторяет GET, а не POST: повторного service.create нет.')

heading('5. Локализация интерфейса и сообщений')
paragraph('SessionLocaleResolver использует английский язык по умолчанию и хранит выбор в сессии. LocaleChangeInterceptor читает lang. Подписи, названия жанров, ошибки Bean Validation, ошибки преобразования типов, flash и страница 404 берутся из resource bundles. Обязательный messages.properties позволяет Spring Boot настроить MessageSource; messages_ru.properties содержит русский вариант. Скриншоты ниже показывают одинаковую ошибку title на обоих языках.')
screenshot('03-empty-title', 'Рисунок 7. Английские подписи и сообщение The title must not be empty.')
screenshot('07-russian-validation', 'Рисунок 8. Русские подписи, жанр и сообщение «Название не может быть пустым».')
listing('Листинг 6. LocaleConfiguration', 'src/main/java/kz/iitu/springlab/config/LocaleConfiguration.java')
listing('Листинг 7. messages.properties — полный bundle', 'src/main/resources/messages.properties')
listing('Листинг 8. messages_ru.properties — полный bundle', 'src/main/resources/messages_ru.properties')

heading('6. Собственное ограничение @NoDigits')
paragraph('@NoDigits имеет обязательные члены message, groups и payload, runtime retention и связь с NoDigitsValidator. null проходит: отсутствие автора проверяет @NotBlank. codePoints(), в отличие от chars(), также проверяет цифры в дополнительных Unicode-плоскостях. Тесты проверяют обычные цифры, арабскую ٢ и математическую 𝟙.')
listing('Листинг 9. Аннотация @NoDigits', 'src/main/java/kz/iitu/springlab/web/validation/NoDigits.java')
listing('Листинг 10. NoDigitsValidator', 'src/main/java/kz/iitu/springlab/web/validation/NoDigitsValidator.java')
screenshot('06-author-digits', 'Рисунок 9. Автор Bloch 2018 отклонён собственным ограничением.')

heading('7. Централизованная обработка исключений')
paragraph('BookService выбрасывает BookNotFoundException для отсутствующего идентификатора. Advice ограничены assignableTypes конкретных контроллеров: это исключает пересечение MVC и REST, поскольку @RestController также является @Controller. Для страницы явно установлен @ResponseStatus(NOT_FOUND): возвращение одного имени шаблона без него дало бы 200. API возвращает RFC 9457 ProblemDetail.')
table(['Запрос', 'Фактический статус / Content-Type', 'Обработчик'], [
    ['GET /books/999?lang=en', '404 · text/html;charset=UTF-8', 'PageExceptionHandler → error/not-found'],
    ['GET /api/books/999?lang=en', '404 · application/problem+json', 'ApiExceptionHandler → ProblemDetail'],
])
code(json.dumps(next(x['body'] for x in json.loads((docs/'browser-checks.json').read_text()) if x.get('request')=='GET /api/books/999?lang=en'), ensure_ascii=False, indent=2), 'json')
listing('Листинг 11. BookNotFoundException', 'src/main/java/kz/iitu/springlab/catalog/BookNotFoundException.java')
listing('Листинг 12. PageExceptionHandler', 'src/main/java/kz/iitu/springlab/web/PageExceptionHandler.java')
listing('Листинг 13. ApiExceptionHandler', 'src/main/java/kz/iitu/springlab/web/ApiExceptionHandler.java')
screenshot('11-mvc-404', 'Рисунок 10. MVC возвращает собственную страницу 404.')
screenshot('12-api-404', 'Рисунок 11. REST возвращает фактический JSON ProblemDetail. Для читаемости изменены только пробелы и отступы JSON.')

heading('8. Индивидуальное задание — вариант 12')
paragraph('Задание: разместить @Size непосредственно на @RequestParam поискового endpoint, показать возникшее исключение и обработать его. Реализован GET /api/books/search?q=…. Длина q должна составлять от 2 до 60 символов включительно; поиск нечувствителен к регистру. Отсутствующий q по умолчанию пуст и отклоняется. Если корректная строка не совпала с названием, возвращается 200 и [].')
paragraph('Встроенная method validation Spring MVC проверяет параметр до вызова search и при нарушении выбрасывает HandlerMethodValidationException. @Validated на классе отсутствует: иначе включился бы иной путь через AOP. Обработчик возвращает 400 application/problem+json, локализованный текст, фактическое имя исключения и errors с параметром q; имя исключения также записывается в журнал.')
listing('Листинг 14. BookRestController, включая поиск варианта 12', 'src/main/java/kz/iitu/springlab/web/BookRestController.java')
table(['Запрос / длина', 'Результат'], [
    ['q=Java', '200, Effective Java'], ['q=eFfEcTiVe', '200, поиск нечувствителен к регистру'],
    ['q отсутствует / 0', '400 HandlerMethodValidationException'], ['q=a / 1', '400 HandlerMethodValidationException'],
    ['q=xx / 2', '200 []'], ['60 символов x', '200 []'], ['61 символ x', '400 HandlerMethodValidationException'],
    ['q=a&lang=ru', '400, русский текст в detail и errors'],
])
checks = json.loads((docs/'browser-checks.json').read_text())
code(json.dumps(next(x['body'] for x in checks if x.get('request')=='GET /api/books/search?q=a'), ensure_ascii=False, indent=2), 'json')
screenshot('13-search-valid', 'Рисунок 12. Корректный запрос q=Java возвращает найденную книгу.')
screenshot('14-search-validation', 'Рисунок 13. q=a: 400 и HandlerMethodValidationException в обработанном ответе.')
screenshot('15-search-validation-ru', 'Рисунок 14. Та же ошибка method validation на русском языке.')

heading('9. Проверка основы лабораторной №5')
paragraph('REST принимает отдельный BookRequest. Новые поля жанра и доступности являются необязательными для старого JSON запроса; это сохраняет команды из методички №5. Идентификатор присваивает репозиторий, PUT использует id из URL, а повторный DELETE возвращает 404.')
table(['Операция', 'Проверенный результат'], [
    ['GET /api/books?author=Bloch&limit=1', '200, JSON содержит Joshua Bloch'],
    ['GET /api/books/{id}', '200 для существующего; 404 ProblemDetail для отсутствующего'],
    ['POST /api/books', '201 + Location; созданный ресурс читается по Location'],
    ['PUT /api/books/{id}', '200 и заменённая запись; 404 для отсутствующего'],
    ['DELETE /api/books/{id}', '204, пустое тело; повторный DELETE 404'],
])
table(['Эксперимент', 'Статус', 'Причина'], [
    ['GET /api/books/abc', '400', 'abc не преобразуется в long @PathVariable'],
    ['GET /api/nothing', '404', 'Нет такого маршрута или статического ресурса'],
    ['DELETE /api/books', '405', 'Метод DELETE не объявлен для пути без id'],
    ['POST /api/books, Content-Type: text/plain', '415', 'Нет подходящего converter для BookRequest из text/plain'],
    ['GET /api/books, Accept: application/xml', '406', 'Не удаётся представить ответ поддерживаемым converter в требуемом формате'],
])
screenshot('01-catalogue', 'Рисунок 15. Каталог и статический CSS; начальные три книги.')
screenshot('02-filter', 'Рисунок 16. Фильтр author=Bloch оставляет одну запись.')

heading('10. Автоматические проверки и воспроизведение')
paragraph('Выполнено bash mvnw -s /workspace/.tools/maven-settings.xml -B verify с Java 25. Команда завершилась BUILD SUCCESS; создан запускаемый JAR. После исправлений повторно выполнен полный набор, затем отдельно проверено повторяемое облачное setup-описание. Сервер запускался из собранного JAR; браузерные проверки выполнены настоящим headless Chromium через Playwright.')
table(['Набор', 'Выполнено', 'Failures / Errors / Skipped'], [
    ['BookWorkflowTests', '25', '0 / 0 / 0'], ['NoDigitsValidatorTests', '6', '0 / 0 / 0'],
    ['SpringLab01ApplicationTests', '1', '0 / 0 / 0'], ['Итого', '32', '0 / 0 / 0'],
])
paragraph('Тесты проверяют не только загрузку контекста: отсутствие записи при ошибках, границы года и поисковой строки, недопустимый enum, нечисловой ввод, русский locale в сессии, однократность flash, сохранение genre/available, запрет подмены id, escaping введённого HTML, REST CRUD и HTTP-ошибки. Браузерные наблюдения сохранены в docs/browser-checks.json; PNG — в docs/screenshots. Проверки демонстрируют техническое выполнение работы; очная демонстрация преподавателю выполняется студентом.')
code('bash mvnw clean verify\njava -jar target/spring-lab-01-0.0.1-SNAPSHOT.jar\n\n# Для подготовленной облачной среды:\nsource /workspace/.tools/java-env.sh\nbash mvnw -s /workspace/.tools/maven-settings.xml -B verify\n\n# Скриншоты (Chromium и Playwright):\npython scripts/capture-evidence.py', 'bash')
paragraph('Для демонстрации используется default profile и порт 8080. Существующий dev profile использует 8081. База данных и секреты не требуются; после перезапуска данные в памяти сбрасываются. Реальная отправка почты для этого задания не требуется. Облачный Maven использует поддерживаемый proxy и существующий system trust store без отключения TLS.')
paragraph('Windows: рабочая папка студента C:\\Labworks\\Spring\\spring-lab-01-main. После получения файлов lab06 и установки JDK 25 выполнить следующие команды PowerShell. Существующую папку и локальные изменения следует сохранить до замены; полный Git-проект можно клонировать в соседнюю новую папку, как описано в README.')
code("Set-Location 'C:\\Labworks\\Spring\\spring-lab-01-main'\n.\\mvnw.cmd clean verify\njava -jar .\\target\\spring-lab-01-0.0.1-SNAPSHOT.jar", 'powershell')

heading('11. Вопросы для защиты')
answers = [
    ('Почему форма отдельно от Book?', 'Правила пользовательского ввода и изменяемое состояние формы отделены от доменной записи; id не участвует в связывании и mass assignment.'),
    ('Что делают th:object и *{title}?', 'th:object выбирает объект модели form; *{title} читает или связывает его свойство title.'),
    ('Что генерирует th:field?', 'name, id, value, selected/checked и служебный hidden marker для checkbox; при ошибке использует rejected value из BindingResult.'),
    ('Зачем пустой объект в GET?', 'Он нужен для оценки th:field и для исходных значений до первого POST.'),
    ('Что если убрать @Valid?', 'Связывание и преобразование типов останутся, но Bean Validation ограничений формы не выполнится.'),
    ('Что если переместить BindingResult после Model?', 'Spring не свяжет его с валидируемым объектом непосредственно перед ним; ошибочная форма может привести к исключению вместо обычного возврата шаблона.'),
    ('Почему genres снова в модели?', 'Список вариантов не приходит в POST и не хранится в BookForm; его нужно предоставить при каждом рендеринге формы.'),
    ('Куда попадают ошибки формы?', 'В BindingResult как FieldError или ObjectError. Контроллер проверяет hasErrors; это отличается от исключения method validation варианта 12.'),
    ('NotNull, NotEmpty, NotBlank?', 'NotNull запрещает null; NotEmpty также пустую строку/коллекцию; NotBlank проверяет строку после учёта пробелов.'),
    ('Откуда текст ошибки?', 'Ключ в message="{book.title.required}" разрешается валидатором через MessageSource и активный Locale; th:errors выводит полученный текст.'),
    ('Field error и global error?', 'Первый относится к конкретному свойству, второй — ко всему объекту, например при class-level constraint. В реализованной форме ограничения дают field errors.'),
    ('Зачем messages.properties?', 'Это обязательный default bundle для автоконфигурации MessageSource и fallback для отсутствующих переводов.'),
    ('Как определяется язык?', 'lang читает LocaleChangeInterceptor; SessionLocaleResolver сохраняет выбор в HTTP-сессии; default — English.'),
    ('Три обязательных члена constraint?', 'message задаёт текст или ключ, groups — группы валидации, payload — дополнительные метаданные нарушения.'),
    ('Почему null допустим для NoDigits?', 'Ограничение отвечает только за цифры; обязательность значения отдельно проверяет NotBlank.'),
    ('Как разделены advice?', 'assignableTypes = BookPageController.class и BookRestController.class. Без ограничения общий обработчик мог бы вернуть неправильный формат ответа.'),
    ('Как выбирается обработчик?', 'Внутри применимого контроллера/advice учитывается наиболее конкретный тип исключения; между advice также важен порядок @Order, а локальные обработчики контроллера проверяются раньше.'),
    ('Чем опасен th:utext?', 'Он вставляет пользовательский HTML без escaping и может привести к XSS. Здесь используется th:text и безопасное связывание th:field.'),
    ('Какое исключение у варианта 12?', 'HandlerMethodValidationException от встроенной Spring MVC validation; ApiExceptionHandler превращает его в 400 ProblemDetail с именем q и локализованным сообщением.'),
]
for question, answer in answers:
    heading(question, 2); paragraph(answer)

heading('12. Выводы')
paragraph('Декларативная валидация позволяет описать правила возле свойств формы и повторно использовать ограничения без ручных if в контроллере. BindingResult связывает нарушения с конкретными полями, сохраняя введённые пользователем данные. Resource bundles отделяют тексты от кода и позволяют менять язык интерфейса и ошибок одновременно. Controller advice и method validation дают согласованные ответы для HTML-клиента и REST API, а Post/Redirect/Get предотвращает повторное создание записи при обновлении страницы.')
heading('13. Источники')
for text in [
    'Методичка Laboratory_work_6_EN.docx — основное задание, вариант 12 и требования к отчёту.',
    'Методичка Laboratory_work_5_EN.docx — восстановление основы REST и MVC каталога.',
    'Spring Framework: https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html',
    'Spring Boot: https://docs.spring.io/spring-boot/reference/features/internationalization.html',
    'Thymeleaf: https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html',
]: paragraph(text)

heading('Приложение. Хранилище и сервис')
listing('Листинг 15. BookRepository', 'src/main/java/kz/iitu/springlab/catalog/BookRepository.java')
listing('Листинг 16. BookService', 'src/main/java/kz/iitu/springlab/catalog/BookService.java')
listing('Листинг 17. BookRequest — совместимость REST с №5', 'src/main/java/kz/iitu/springlab/web/BookRequest.java')

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
    ('\n\nЛАБОРАТОРНАЯ РАБОТА №6',22),
    ('Forms and validation',18),
    ('Thymeleaf · Bean Validation · i18n\nController advice · Method validation',12),
    ('\nКурс: RWPSF 3305\nWeb Application Development with Spring Framework',12),
    ('\nВыполнил: Kassymzhanov Arzum\nГруппа: IT1-2404IS\nВариант: 12 — Method validation',13),
    ('\n\nAlmaty, 2026',12),
]:
    par=doc.add_paragraph();par.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=par.add_run(text);run.font.size=Pt(size)
doc.add_page_break()
md=['# Лабораторная работа №6 — Kassymzhanov Arzum\n\nIT1-2404IS · Вариант 12\n']
parts=['<section class="cover"><h2>International Information Technology University</h2><p>Department of Information Systems</p><h1>ЛАБОРАТОРНАЯ РАБОТА №6</h1><h2>Forms and validation</h2><p>RWPSF 3305 — Web Application Development with Spring Framework</p><p>Kassymzhanov Arzum<br>IT1-2404IS<br>Вариант 12 — Method validation</p><p>Almaty, 2026</p></section>']
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
(docs/'report.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Lab06 — Kassymzhanov Arzum</title><style>'+style+'</style></head><body>'+''.join(parts)+'</body></html>')
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
