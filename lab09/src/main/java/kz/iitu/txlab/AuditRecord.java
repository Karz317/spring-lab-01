package kz.iitu.txlab;
import jakarta.persistence.*;
import java.time.Instant;
@Entity @Table(name = "audit_records")
public class AuditRecord {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;
    @Column(nullable = false, length = 250) private String message;
    @Column(name = "created_at", nullable = false) private Instant createdAt;
    protected AuditRecord() {}
    public AuditRecord(String message) { this.message = message; this.createdAt = Instant.now(); }
    public Long getId() { return id; }
    public String getMessage() { return message; }
    public Instant getCreatedAt() { return createdAt; }
}
