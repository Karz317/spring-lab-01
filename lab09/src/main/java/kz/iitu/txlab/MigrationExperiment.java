package kz.iitu.txlab;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationVersion;
import org.springframework.stereotype.Service;
import java.sql.*;
import java.util.*;
@Service
public class MigrationExperiment {
    public Map<String,Object> run() throws SQLException {
        String url = "jdbc:h2:mem:migration_" + UUID.randomUUID() + ";DB_CLOSE_DELAY=-1";
        try {
            Flyway first = Flyway.configure().dataSource(url, "sa", "").target(MigrationVersion.fromVersion("2")).load();
            int initial = first.migrate().migrationsExecuted;
            // A fresh Flyway instance represents initialization on the next application start.
            int restart = Flyway.configure().dataSource(url, "sa", "").target(MigrationVersion.fromVersion("2")).load().migrate().migrationsExecuted;
            Flyway upgrade = Flyway.configure().dataSource(url, "sa", "").load();
            int added = upgrade.migrate().migrationsExecuted;
            List<Map<String,Object>> history = new ArrayList<>();
            try (Connection c = DriverManager.getConnection(url,"sa", ""); Statement s=c.createStatement();
                 ResultSet r=s.executeQuery("SELECT \"version\", \"script\", \"success\", \"checksum\" FROM \"flyway_schema_history\" WHERE \"version\" IS NOT NULL ORDER BY \"installed_rank\"")) {
                while(r.next()) history.add(Map.of("version",r.getString(1),"script",r.getString(2),"state",r.getBoolean(3)?"SUCCESS":"FAILED","checksum",r.getInt(4)));
            }
            boolean index;
            try (Connection c = DriverManager.getConnection(url,"sa", ""); ResultSet r = c.getMetaData().getIndexInfo(null, "PUBLIC", "ACCOUNTS", false, false)) {
                index = false; while (r.next()) if ("IDX_ACCOUNTS_OWNER_NAME".equals(r.getString("INDEX_NAME"))) index = true;
            }
            return Map.of("emptyDatabaseApplied", initial, "restartApplied", restart, "upgradeApplied", added, "indexPresent", index, "history", history);
        } finally {
            try (Connection c = DriverManager.getConnection(url, "sa", ""); Statement s = c.createStatement()) { s.execute("SHUTDOWN"); }
        }
    }
}
