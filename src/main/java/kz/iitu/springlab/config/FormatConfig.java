package kz.iitu.springlab.config;

import java.time.format.DateTimeFormatter;
import java.util.Locale;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class FormatConfig {

    @Bean
    public DateTimeFormatter reportDateFormatter(
            @Value("${app.date-pattern:dd.MM.yyyy HH:mm:ss}") String pattern) {

        return DateTimeFormatter.ofPattern(pattern, Locale.ENGLISH);
    }
}
