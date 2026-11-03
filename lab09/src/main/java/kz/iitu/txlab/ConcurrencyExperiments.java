package kz.iitu.txlab;
import jakarta.persistence.*;
import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.*;
import java.util.*;
import org.springframework.stereotype.Service;
@Service
public class ConcurrencyExperiments {
    private final DataSource dataSource;
    private final EntityManagerFactory emf;
    public ConcurrencyExperiments(DataSource dataSource, EntityManagerFactory emf) { this.dataSource = dataSource; this.emf = emf; }
    public Map<String,Object> isolation(int isolation) throws SQLException {
        // Separate real connections bypass Hibernate's first-level entity cache.
        try (Connection reader = dataSource.getConnection(); Connection writer = dataSource.getConnection()) {
            reader.setTransactionIsolation(isolation); reader.setAutoCommit(false);
            writer.setAutoCommit(false);
            BigDecimal first = read(reader);
            try (PreparedStatement sql = writer.prepareStatement("UPDATE accounts SET balance = balance + 50, version = version + 1 WHERE id = 1")) { sql.executeUpdate(); }
            writer.commit();
            BigDecimal second = read(reader); reader.commit();
            return Map.of("isolation", isolation == Connection.TRANSACTION_READ_COMMITTED ? "READ_COMMITTED" : "REPEATABLE_READ", "firstRead", first, "secondRead", second, "writerCommitted", read(writer), "database", reader.getMetaData().getDatabaseProductVersion());
        }
    }
    private BigDecimal read(Connection c) throws SQLException {
        try (Statement s = c.createStatement(); ResultSet r = s.executeQuery("SELECT balance FROM accounts WHERE id = 1")) { r.next(); return r.getBigDecimal(1); }
    }
    public Map<String,Object> optimisticLock() {
        EntityManager first = emf.createEntityManager(), second = emf.createEntityManager();
        try {
            first.getTransaction().begin(); second.getTransaction().begin();
            Account a = first.find(Account.class, 1L), b = second.find(Account.class, 1L);
            long loadedVersion = b.getVersion();
            a.credit(new BigDecimal("10.00")); first.getTransaction().commit();
            b.credit(new BigDecimal("20.00"));
            String conflict;
            try { second.getTransaction().commit(); throw new IllegalStateException("Stale update unexpectedly succeeded"); }
            catch (RollbackException | OptimisticLockException ex) {
                Throwable cause = ex; boolean optimistic = false;
                while (cause != null) { if (cause instanceof OptimisticLockException || cause.getClass().getSimpleName().contains("Stale")) optimistic = true; cause = cause.getCause(); }
                if (!optimistic) throw ex;
                conflict = ex.getClass().getSimpleName();
            }
            first.clear(); Account saved = first.find(Account.class, 1L);
            return Map.of("loadedVersion", loadedVersion, "committedVersion", saved.getVersion(), "finalBalance", saved.getBalance(), "conflict", conflict, "staleUpdateRejected", true);
        } finally {
            if (first.getTransaction().isActive()) first.getTransaction().rollback();
            if (second.getTransaction().isActive()) second.getTransaction().rollback();
            first.close(); second.close();
        }
    }
}
