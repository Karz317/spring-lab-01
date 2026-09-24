package kz.iitu.springlab.notify;

import org.springframework.context.annotation.Fallback;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

@Component("noop")
@Fallback
@Order(99)
public class NoopNotifier implements Notifier {

    @Override
    public String send(String message) {
        return "noop";
    }

    @Override
    public String channel() {
        return "noop";
    }
}
