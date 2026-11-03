package kz.iitu.txlab;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.*;
@Service
public class AuditService {
    private final AuditRepository repository;
    public AuditService(AuditRepository repository) { this.repository = repository; }
    @Transactional(propagation = Propagation.REQUIRED)
    public void required(String message) { repository.saveAndFlush(new AuditRecord(message)); }
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void requiresNew(String message) { repository.saveAndFlush(new AuditRecord(message)); }
}
