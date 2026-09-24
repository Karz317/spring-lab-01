package kz.iitu.springlab.web;

import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import kz.iitu.springlab.scope.TicketOffice;

@RestController
@RequestMapping("/api/lab3")
public class ScopeController {

    private final TicketOffice office;

    public ScopeController(TicketOffice office) {
        this.office = office;
    }


    @GetMapping("/scope")
    public Map<String, Object> scope() {

        return office.demo();
    }
}