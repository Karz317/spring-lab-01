# Laboratory Work 09 — Spring Transactions and Schema Versioning

Arzum Kassymzhanov · IT1-2404IS · 3 November 2026.

This standalone Maven module uses **Spring Boot 3.5.16**, Java 17 bytecode,
Spring Data JPA, **H2 2.3.232** and Flyway. It is separate from the existing
Spring Boot 4 book application so earlier laboratory work remains available.
Verification was performed with JDK 25.0.2 and Maven 3.9.16.

## Build and run

From the repository root:

```powershell
Set-Location .\lab09
.\mvnw.cmd clean verify
java -jar .\target\transaction-lab09-1.0.0.jar
```

Open <http://127.0.0.1:8089>. The three views display actual results returned
by `POST /api/lab09/experiments`. Press **Run all experiments** once, then
switch views. The service binds to loopback only. The demo endpoint resets
Alice and Bob before each scenario and restores their initial balances at
the end; use it only with the disposable lab database.

Default database: `jdbc:h2:mem:txlab;DB_CLOSE_DELAY=-1`, username `sa`, empty
password. Hibernate validates the schema; Flyway owns DDL. H2 console is at
`/h2-console`. Liquibase is not installed.

For a persistent lab database:

```powershell
java -jar .\target\transaction-lab09-1.0.0.jar '--spring.datasource.url=jdbc:h2:file:./data/txlab'
```

## Implemented experiments

| Task | Actual result |
| --- | --- |
| A: transfer 100.00 | Alice 900.00, Bob 600.00, sum 1500.00 |
| A: insufficient funds / unchecked exception after flushed debit | Both balances unchanged |
| A: checked exception | Debit committed by default; rolled back with `rollbackFor` |
| B: REQUIRED / REQUIRES_NEW audit | 0 / 1 audit row after outer rollback |
| C: READ_COMMITTED / REPEATABLE_READ on H2 | Second read 1050.00 / 1000.00 |
| D: two independent EntityManagers | Stale commit rejected, balance 1010.00, version 1 |
| E: initial V1–V2 / restart / upgrade | 2 / 0 / 2 migrations; V3 index and V4 audit table |

`ConcurrencyExperiments` uses two independent JDBC connections for isolation
so JPA's first-level cache cannot conceal a non-repeatable read. Optimistic
locking uses two simultaneously active, independent persistence contexts.
`AuditService` is a separate bean, so propagation is applied by Spring's proxy.

## Verify real application restarts

Stop any instance on port 8089, then run:

```powershell
.\scripts\verify-migrations.ps1
# Add -KeepRunning to leave the final instance available for inspection.
```

The script starts the **actual application three times against the same H2
file**: target V2 on an empty database; target V2 again; then target V4.
At V2, `ddl-auto=none` deliberately permits the pre-audit schema. The final
startup uses `ddl-auto=validate`. Logs and observations are saved under a
unique `target/migration-restart-*` directory. It does not delete an existing
database. Use the printed PID to stop the final instance when using `-KeepRunning`.

## Tests and evidence

18 integration tests passed, with 0 failures, 0 errors and 0 skipped tests.
Tests use real Spring beans, transactions, HTTP requests and H2, with no mocks.
Run results are written to `target/lab09-observations.json` and Surefire reports.

- [Report](docs/Lab09_Kassymzhanov_Arzum.docx)
- [Live API observations](docs/evidence/live-observations.json)
- [Surefire summary](docs/evidence/surefire-summary.txt)
- [Successful Maven log](docs/evidence/maven-verify.log)
- [First V2 startup](docs/evidence/first-v2.log)
- [V2 restart](docs/evidence/restart-v2.log)
- [Upgrade to V4](docs/evidence/upgrade-v4.log)
- [HTTP requests](requests/lab09.http)

Report figures are rendered excerpts of actual JSON responses and logs.

## Source map

`Account`, `AccountRepository`, `TransferService`: entity, `@Version`, transfer,
rollback rules. `AuditRecord`, `AuditRepository`, `AuditService`,
`PropagationService`: inner audit and outer rollback. `ConcurrencyExperiments`:
isolation and optimistic locking. `MigrationExperiment`: Flyway lifecycle and
SQL inspection of `flyway_schema_history`. `TransactionLabTests`: assertions
for all tasks plus input validation and HTTP behavior.

## References

- [Spring transactions](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
- [Spring propagation](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)
- [H2 transaction isolation](https://h2database.com/html/advanced.html#transaction_isolation)
