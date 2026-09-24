package kz.iitu.springlab.scope;

import java.util.UUID;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

@Component
@Scope("prototype")
public class Ticket {

    private final String id =
            UUID.randomUUID().toString().substring(0, 8);

    public String id() {
        return id;
    }
}