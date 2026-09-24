package kz.iitu.springlab.config;

import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

@Component
@Profile("!dev & !prod")
public class DefaultBanner implements EnvironmentBanner {

    @Override
    public String describe() {
        return "no profile is active";
    }
}