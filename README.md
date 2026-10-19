# Spring Laboratory 07 - REST API Design

**Kassymzhanov Arzum - IT1-2404IS - Variant 12 (RestTestClient).**

The `lab07` branch implements a documented REST API for the `Book` resource. It
continues the previous laboratory work and preserves the MVC catalogue,
localization, validation and earlier tests.

## Run and verify

The project uses JDK 25 and the Maven wrapper.

```powershell
Set-Location 'C:\Labworks\Spring\spring-lab-01-main'
.\mvnw.cmd clean verify
java -jar .\target\spring-lab-01-0.0.1-SNAPSHOT.jar
```

The default profile runs on port `8080`. Application data is stored in memory and
is restored to three sample books after each restart.

## REST contract

| Method | Path | Success |
| --- | --- | --- |
| GET | `/api/books` | `200` and `List<BookResponse>` |
| GET | `/api/books/{id}` | `200`, or `404` Problem Detail |
| POST | `/api/books` | `201`, `Location`, and `BookResponse` |
| PUT | `/api/books/{id}` | `200`, or `400` / `404` / `409` |
| DELETE | `/api/books/{id}` | `204`, or `404` |
| GET | `/api/books/search?q=...` | `200`, or `400` method validation |

`BookRequest` accepts only `title`, `author`, `year` and `genre`. `BookResponse`
adds the server-owned `id` and `createdAt` fields. Invalid bodies, missing books,
duplicates and invalid search parameters are returned as
`application/problem+json`.

## OpenAPI

With the application running:

- Swagger UI: <http://localhost:8080/swagger-ui.html>
- OpenAPI JSON: <http://localhost:8080/v3/api-docs>

## Variant 12

`BookApiRestTestClientTests` contains the three required tests:

1. creation returns `201` and a `Location` header;
2. a missing book returns a `404` Problem Detail;
3. deletion returns `204` with an empty body.

The complete suite contains **36 tests** with no failures or errors.

## Evidence and report

- [Laboratory report](docs/Lab07_Kassymzhanov_Arzum.docx)
- [Laboratory report (PDF)](docs/Lab07_Kassymzhanov_Arzum.pdf)
- [Live HTTP observations](docs/lab07-observations.json)
- [Browser screenshots](docs/screenshots/lab07)
- [IDE HTTP client requests](requests/lab07.http)

To recapture the live evidence against a disposable local instance:

```powershell
python scripts/capture-lab07-evidence.py
```

To regenerate the report after updating source files or screenshots:

```powershell
python scripts/generate-lab07-report.py
```
