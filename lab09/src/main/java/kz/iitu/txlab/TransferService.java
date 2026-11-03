package kz.iitu.txlab;
import java.math.BigDecimal;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
@Service
public class TransferService {
    private final AccountRepository repository;
    public TransferService(AccountRepository repository) { this.repository = repository; }
    @Transactional
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        if (fromId.equals(toId)) throw new IllegalArgumentException("Accounts must be different");
        Account from = get(fromId); Account to = get(toId);
        from.debit(amount); to.credit(amount);
        repository.save(from); repository.save(to);
    }
    @Transactional
    public void failAfterDebit(Long id, BigDecimal amount) {
        get(id).debit(amount);
        repository.flush(); // Prove rollback even after SQL UPDATE has reached the database.
        throw new IllegalStateException("Simulated unchecked failure after debit");
    }
    @Transactional
    public void checkedDefault(Long id, BigDecimal amount) throws CheckedTransferException {
        get(id).debit(amount); repository.flush();
        throw new CheckedTransferException();
    }
    @Transactional(rollbackFor = CheckedTransferException.class)
    public void checkedRollback(Long id, BigDecimal amount) throws CheckedTransferException {
        get(id).debit(amount); repository.flush();
        throw new CheckedTransferException();
    }
    private Account get(Long id) { return repository.findById(id).orElseThrow(() -> new IllegalArgumentException("Account not found: " + id)); }
    public static class CheckedTransferException extends Exception {
        public CheckedTransferException() { super("Simulated checked failure after debit"); }
    }
}
