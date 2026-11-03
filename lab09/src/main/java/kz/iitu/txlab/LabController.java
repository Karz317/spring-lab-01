package kz.iitu.txlab;
import java.math.BigDecimal;
import java.util.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.web.bind.annotation.*;
@RestController
@RequestMapping("/api/lab09")
public class LabController {
    private final LabExperiments experiments;
    private final TransferService transfers;
    public LabController(LabExperiments experiments,TransferService transfers) { this.experiments=experiments; this.transfers=transfers; }
    @GetMapping("/accounts") public List<Map<String,Object>> accounts() { return experiments.accounts(); }
    @PostMapping("/transfers") public List<Map<String,Object>> transfer(@Valid @RequestBody TransferRequest request) {
        transfers.transfer(request.fromId(),request.toId(),request.amount()); return experiments.accounts();
    }
    @PostMapping("/experiments") public Map<String,Object> run() throws Exception { return experiments.runAll(); }
    public record TransferRequest(@NotNull @Positive Long fromId,@NotNull @Positive Long toId,@NotNull @DecimalMin("0.01") @Digits(integer=17,fraction=2) BigDecimal amount) {}
}
