package kz.iitu.springlab.scope;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Component;

@Component
public class TicketOffice {

    private final Ticket direct;
    private final ObjectProvider<Ticket> provider;

    public TicketOffice(
            Ticket direct,
            ObjectProvider<Ticket> provider) {

        this.direct = direct;
        this.provider = provider;
    }

    public Map<String, Object> demo() {

        String direct1 = direct.id();
        String direct2 = direct.id();

        String fresh1 = provider.getObject().id();
        String fresh2 = provider.getObject().id();

        return Map.of(
                "injectedDirectly", List.of(direct1, direct2),
                "viaProvider", List.of(fresh1, fresh2),
                "office", System.identityHashCode(this)
        );
    }
}
