package kz.iitu.txlab;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.math.BigDecimal;
import java.sql.Connection;
import java.nio.file.*;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.*;
@SpringBootTest(webEnvironment=SpringBootTest.WebEnvironment.RANDOM_PORT)
class TransactionLabTests {
    @Autowired TransferService transfers;
    @Autowired PropagationService propagation;
    @Autowired ConcurrencyExperiments concurrency;
    @Autowired MigrationExperiment migrations;
    @Autowired LabExperiments experiments;
    @Autowired JdbcTemplate jdbc;
    @Autowired ObjectMapper mapper;
    @Autowired TestRestTemplate http;
    @BeforeEach void reset() { experiments.reset(); }
    BigDecimal balance(long id) { return jdbc.queryForObject("SELECT balance FROM accounts WHERE id=?",BigDecimal.class,id); }
    void money(String expected,long id) { assertEquals(0,new BigDecimal(expected).compareTo(balance(id))); }
    @Test void successfulTransferIsAtomicAndConservesMoney() {
        transfers.transfer(1L,2L,new BigDecimal("100.00")); money("900",1); money("600",2);
        assertEquals(0,new BigDecimal("1500").compareTo(balance(1).add(balance(2))));
    }
    @Test void insufficientFundsChangesNeitherAccount() {
        assertThrows(IllegalStateException.class,()->transfers.transfer(1L,2L,new BigDecimal("1001.00"))); money("1000",1); money("500",2);
    }
    @Test void uncheckedFailureRollsBackFlushedDebit() {
        assertThrows(IllegalStateException.class,()->transfers.failAfterDebit(1L,new BigDecimal("100.00"))); money("1000",1); money("500",2);
    }
    @Test void checkedExceptionCommitsByDefault() {
        assertThrows(TransferService.CheckedTransferException.class,()->transfers.checkedDefault(1L,new BigDecimal("100.00"))); money("900",1);
    }
    @Test void rollbackForRollsBackCheckedException() {
        assertThrows(TransferService.CheckedTransferException.class,()->transfers.checkedRollback(1L,new BigDecimal("100.00"))); money("1000",1);
    }
    @Test void requiredAuditRollsBackWithOuter() {
        assertThrows(IllegalStateException.class,()->propagation.outer(false)); assertEquals(0,experiments.auditCount()); money("1000",1);
    }
    @Test void requiresNewAuditSurvivesOuterRollback() {
        assertThrows(IllegalStateException.class,()->propagation.outer(true)); assertEquals(1,experiments.auditCount()); money("1000",1);
    }
    @Test void readCommittedSeesCommittedChangeOnSecondRead() throws Exception {
        var r=concurrency.isolation(Connection.TRANSACTION_READ_COMMITTED);
        assertEquals(new BigDecimal("1000.00"),r.get("firstRead")); assertEquals(new BigDecimal("1050.00"),r.get("secondRead"));
    }
    @Test void repeatableReadKeepsSnapshotOnH2() throws Exception {
        var r=concurrency.isolation(Connection.TRANSACTION_REPEATABLE_READ);
        assertEquals(r.get("firstRead"),r.get("secondRead")); assertEquals(new BigDecimal("1050.00"),r.get("writerCommitted"));
    }
    @Test void staleEntityCannotOverwriteCommittedUpdate() {
        var r=concurrency.optimisticLock(); assertEquals(true,r.get("staleUpdateRejected")); assertEquals(0L,r.get("loadedVersion")); assertEquals(1L,r.get("committedVersion")); money("1010",1);
    }
    @Test void migrationsApplyOnceAndNewVersionsAreAdded() throws Exception {
        var r=migrations.run(); assertEquals(2,r.get("emptyDatabaseApplied")); assertEquals(0,r.get("restartApplied")); assertEquals(2,r.get("upgradeApplied")); assertEquals(true,r.get("indexPresent"));
    }
    @Test void sameAccountTransferIsRejected() {
        assertThrows(IllegalArgumentException.class,()->transfers.transfer(1L,1L,BigDecimal.ONE)); money("1000",1);
    }
    @Test void missingDestinationDoesNotDebitSource() {
        assertThrows(IllegalArgumentException.class,()->transfers.transfer(1L,999L,BigDecimal.ONE)); money("1000",1);
    }
    @Test void fractionalCentsAreRejected() {
        assertThrows(IllegalArgumentException.class,()->transfers.transfer(1L,2L,new BigDecimal("1.001"))); money("1000",1);
    }
    @Test void inactiveDestinationRollsBackSourceDebit() {
        jdbc.update("UPDATE accounts SET status='BLOCKED' WHERE id=2");
        assertThrows(IllegalStateException.class,()->transfers.transfer(1L,2L,BigDecimal.ONE)); money("1000",1); money("500",2);
    }
    @Test void apiReturns400ForInvalidAmount() {
        var response=http.postForEntity("/api/lab09/transfers",Map.of("fromId",1,"toId",2,"amount",-1),String.class);
        assertEquals(HttpStatus.BAD_REQUEST,response.getStatusCode()); money("1000",1);
    }
    @Test void apiReturns409ForInsufficientFunds() {
        var response=http.postForEntity("/api/lab09/transfers",Map.of("fromId",1,"toId",2,"amount",1001),String.class);
        assertEquals(HttpStatus.CONFLICT,response.getStatusCode()); money("1000",1);
    }
    @Test void saveMeasuredEvidence() throws Exception {
        var evidence=experiments.runAll();
        Path path=Path.of("target","lab09-observations.json"); Files.createDirectories(path.getParent());
        mapper.writerWithDefaultPrettyPrinter().writeValue(path.toFile(),evidence);
        assertTrue(Files.size(path)>1000);
    }
}
