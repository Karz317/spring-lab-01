package kz.iitu.txlab;
import java.math.BigDecimal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
@Service
public class PropagationService {
    private final AuditService audit;
    private final AccountRepository accounts;
    public PropagationService(AuditService audit, AccountRepository accounts) { this.audit = audit; this.accounts = accounts; }
    @Transactional
    public void outer(boolean independentAudit) {
        accounts.findById(1L).orElseThrow().debit(new BigDecimal("10.00"));
        accounts.flush();
        // Separate Spring bean: the call crosses the transaction proxy.
        if (independentAudit) audit.requiresNew("REQUIRES_NEW inner committed");
        else audit.required("REQUIRED participates in outer");
        throw new IllegalStateException("Outer failed after audit returned");
    }
}
