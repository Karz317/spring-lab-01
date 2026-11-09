# Spring Laboratory Works

## Laboratory 10 — Spring Security

The catalogue uses form login backed by PostgreSQL 16, BCrypt, role checks
and CSRF protection. Flyway applies the original V1–V4 scripts and adds
`V5__security.sql`. Hibernate validates the schema. The catalogue continues
to use the earlier in-memory book repository; users and roles are persisted.

From the repository root, use JDK 25 and Maven. With Docker running:

```powershell
$env:SPRINGLAB_DB_PASSWORD = Read-Host 'Choose a password for the local lab database'
docker compose up -d db
.\mvnw.cmd clean verify
java -jar .\target\spring-lab-01-0.0.1-SNAPSHOT.jar
```

Open <http://127.0.0.1:8080/books>. The demo accounts are `user / user123`
and `admin / admin123`. The application's database password is separate.
For an existing PostgreSQL installation, create a database named `springlab`
and set `SPRINGLAB_DB_URL`, `SPRINGLAB_DB_USER` and
`SPRINGLAB_DB_PASSWORD` to match it. Use a lab database that the account can
migrate; startup binds to loopback.

### Demonstration

1. In a signed-out browser, open `/books`. The application returns
   `302 /login`; the browser then displays the generated login form.
2. Sign in as `user` and try `/admin`: expect `403`. Sign in as `admin`
   in another browser session: `/admin` returns `200` and shows usernames,
   roles and enabled state. Only the administrator can create, edit or
   delete books; the existing `PUT /api/books/{id}` handles editing.
3. In a database client, run `SELECT username, password_hash FROM app_user;`.
4. As admin, open `/books/new` and look for `name="_csrf"` in its HTML.
   In browser developer tools, remove the hidden input before submitting a
   valid form: expect `403`. Reload the form and submit it unchanged:
   expect `302 /books` and a new book. Keep the session the same in both
   requests. The login form itself also requires CSRF.
5. Run `.\mvnw.cmd '-Dtest=Variant12SecurityTests' test` for the three
   access tests (`302`, `403`, `200`). The full suite also covers actual
   authentication, account disabling, method security, and CSRF.

The full Maven suite passed **42 tests** with H2 in PostgreSQL compatibility
mode. The [live browser and SQL results](docs/lab10/live-observations.json)
were recorded separately against PostgreSQL 16.14.

The following sections document earlier branches and exercises.

## Laboratory 09 — Transactions and schema versioning

The `lab09` branch adds a standalone **Spring Boot 3** module at
[`lab09/`](lab09/README.md): account transfers, rollback and propagation,
H2 isolation experiments, optimistic locking and Flyway migrations.
All **18 integration tests pass**. The module includes a seven-page
[report](lab09/docs/Lab09_Kassymzhanov_Arzum.docx), a
[PDF copy](lab09/docs/Lab09_Kassymzhanov_Arzum.pdf), measured API responses
and actual application restart logs.

```powershell
Set-Location .\lab09
.\mvnw.cmd clean verify
java -jar .\target\transaction-lab09-1.0.0.jar
```

The local demonstration runs at <http://127.0.0.1:8089>.

## Laboratory 07 - REST API Design

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
