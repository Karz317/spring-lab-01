# Spring laboratory 06 — forms and validation

**Kassymzhanov Arzum · IT1-2404IS · Variant 12 (method validation).**

The `lab06` branch continues `lab04`, restores the catalogue required by laboratory 5,
and implements laboratory 6. Previous lab controllers and aspects are preserved.

## Run and verify

Requires JDK **25**. The repository wrapper installs Maven 3.9.16.

```bash
bash mvnw clean verify
java -jar target/spring-lab-01-0.0.1-SNAPSHOT.jar
```

Use the default profile (port **8080**); the existing `dev` profile uses **8081**.

On Windows, with the updated files in your directory and JDK 25 on PATH:

```powershell
Set-Location 'C:\Labworks\Spring\spring-lab-01-main'
.\mvnw.cmd clean verify
java -jar .\target\spring-lab-01-0.0.1-SNAPSHOT.jar
```

If this folder contains a downloaded `main` ZIP, it does not have Git history.
The delivered project ZIP contains `lab06` files; preserve your existing folder
before replacing it. To obtain the Git history, clone the `lab06` branch into a
new folder:

```powershell
git clone --branch lab06 https://github.com/Karz317/spring-lab-01.git C:\Labworks\Spring\spring-lab-01-lab06
```

Open `/books` and `/books/new` on the running server. Data is held in memory;
restarting restores three example books. The form persists genre and availability
along with title, author and year. A separate `BookRequest` keeps the old REST JSON
(`title`, `author`, `year`) working: omitted genre defaults to TECHNOLOGY and omitted
availability defaults to true. Client-supplied IDs cannot overwrite stored records.

In this cloud environment:

```bash
source /workspace/.tools/java-env.sh
bash mvnw -s /workspace/.tools/maven-settings.xml clean verify
java -jar target/spring-lab-01-0.0.1-SNAPSHOT.jar
```

The external Java/Maven configuration uses the platform HTTPS proxy and the existing
system Java trust store. TLS and archive checksum verification stay enabled.

## What to demonstrate

1. Open `/books/new`; submit an empty title, year 1200, and an empty genre.
   Errors appear next to fields and in the summary. The other entered values remain.
2. Enter `Bloch 2018` as the author: the custom `@NoDigits` constraint rejects it.
3. Switch between `?lang=en` and `?lang=ru`. Labels, genres, validation errors,
   flash messages and not-found pages use resource bundles; the locale persists in the session.
4. Submit valid data: POST responds 302, followed by GET `/books` (200).
   Refresh consumes no new POST and creates no duplicate. The flash message appears once.
5. Request `/books/999` (404 HTML) and `/api/books/999` (404 application/problem+json).
6. Demonstrate variant 12 with `/api/books/search?q=Java` (200), `?q=a` (400),
   and a 61-character query (400). Valid unmatched searches return an empty array.

## Variant 12

`@Size(min = 2, max = 60)` is placed directly on the `@RequestParam String q` in
`BookRestController.search`. Spring MVC built-in method validation throws
`HandlerMethodValidationException` before the method executes. There is no class-level
`@Validated`, so this uses MVC validation rather than AOP method validation.
`ApiExceptionHandler` handles the exception, logs its actual type, and returns a
localized 400 ProblemDetail including `exception` and parameter errors.

`BindingResult` in the book form is different: validation failures are collected
beside the form argument and the controller redisplays the template without an exception.

## Evidence and report

- [Full report](docs/Lab06_Kassymzhanov_Arzum.docx)
- [Report text](docs/report.md)
- [Real browser screenshots](docs/screenshots)
- [Browser and HTTP observations](docs/browser-checks.json)
- [IDE HTTP client requests](requests/lab06.http)

The report includes actual browser captures, source listings, the English and Russian
bundles, response tables and answers for the defence. To recreate screenshots with
a locally installed Chromium:

```bash
python -m pip install playwright
python scripts/capture-evidence.py --chromium /usr/bin/chromium
```

The screenshot script submits one valid demonstration book and creates/deletes a
temporary REST book. Run it against a disposable in-memory demonstration instance.

To regenerate DOCX and PDF from the current source and PNG evidence:

```bash
python -m pip install python-docx playwright
python scripts/generate-report.py
```

The report generator requires a local Chromium executable at `/usr/bin/chromium`.
