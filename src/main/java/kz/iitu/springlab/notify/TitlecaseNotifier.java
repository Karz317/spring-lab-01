package kz.iitu.springlab.notify;

import java.util.Arrays;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;

@Component("titlecase")
@Order(3)
public class TitlecaseNotifier implements Notifier {

    private static final Logger log =
            LoggerFactory.getLogger(TitlecaseNotifier.class);

    @PostConstruct
    public void init() {
        log.info("TITLECASE NOTIFIER >> initialized");
    }

    @Override
    public String send(String message) {
        if (message == null || message.isBlank()) {
            return message;
        }

        return Arrays.stream(message.trim().split("\\s+"))
                .map(word ->
                        Character.toUpperCase(word.charAt(0))
                                + word.substring(1))
                .collect(Collectors.joining(" "));
    }

    @Override
    public String channel() {
        return "titlecase";
    }
}
