package kz.iitu.txlab;
import java.math.BigDecimal;
import java.sql.Connection;
import java.util.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
@Service
public class LabExperiments {
    private final TransferService transfers;
    private final PropagationService propagation;
    private final ConcurrencyExperiments concurrency;
    private final MigrationExperiment migrations;
    private final JdbcTemplate jdbc;
    public LabExperiments(TransferService transfers, PropagationService propagation, ConcurrencyExperiments concurrency, MigrationExperiment migrations, JdbcTemplate jdbc) {
        this.transfers=transfers; this.propagation=propagation; this.concurrency=concurrency; this.migrations=migrations; this.jdbc=jdbc;
    }
    public void reset() {
        jdbc.update("DELETE FROM audit_records");
        jdbc.update("UPDATE accounts SET balance=CASE WHEN id=1 THEN 1000.00 ELSE 500.00 END, version=0, status='ACTIVE' WHERE id IN (1,2)");
    }
    public List<Map<String,Object>> accounts() { return jdbc.queryForList("SELECT id, owner_name, balance, version, status FROM accounts ORDER BY id"); }
    public synchronized Map<String,Object> runAll() throws Exception {
        // Local teaching demo only; resets the two seeded accounts before each experiment.
        Map<String,Object> result = new LinkedHashMap<>();
        reset(); var before=accounts(); transfers.transfer(1L,2L,new BigDecimal("100.00"));
        result.put("transfer", Map.of("before", before,"after",accounts(),"amount","100.00"));
        reset(); String insufficient = expectFailure(() -> transfers.transfer(1L,2L,new BigDecimal("1001.00")));
        result.put("insufficientFunds",Map.of("exception",insufficient,"after",accounts()));
        reset(); String unchecked = expectFailure(() -> transfers.failAfterDebit(1L,new BigDecimal("100.00")));
        result.put("rollback",Map.of("exception",unchecked,"after",accounts(),"sqlFlushedBeforeFailure",true));
        reset(); try { transfers.checkedDefault(1L,new BigDecimal("100.00")); } catch (TransferService.CheckedTransferException expected) { }
        result.put("checkedDefault",accounts());
        reset(); try { transfers.checkedRollback(1L,new BigDecimal("100.00")); } catch (TransferService.CheckedTransferException expected) { }
        result.put("checkedRollbackFor",accounts());
        reset(); expectFailure(() -> propagation.outer(false));
        result.put("required",Map.of("auditCount",auditCount(),"accounts",accounts()));
        reset(); expectFailure(() -> propagation.outer(true));
        result.put("requiresNew",Map.of("auditCount",auditCount(),"accounts",accounts()));
        reset(); result.put("readCommitted",concurrency.isolation(Connection.TRANSACTION_READ_COMMITTED));
        reset(); result.put("repeatableRead",concurrency.isolation(Connection.TRANSACTION_REPEATABLE_READ));
        reset(); result.put("optimisticLock",concurrency.optimisticLock());
        result.put("migrations",migrations.run());
        result.put("runtime",Map.of("java",System.getProperty("java.version"),"springBoot",org.springframework.boot.SpringBootVersion.getVersion(),"database",jdbc.queryForObject("SELECT H2VERSION()",String.class)));
        reset(); return result;
    }
    public long auditCount() { return jdbc.queryForObject("SELECT COUNT(*) FROM audit_records",Long.class); }
    private String expectFailure(Runnable action) {
        try { action.run(); } catch (IllegalStateException expected) { return expected.getMessage(); }
        throw new AssertionError("Expected an IllegalStateException");
    }
}
