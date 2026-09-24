package kz.iitu.springlab.config;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

@Validated
@ConfigurationProperties(prefix = "app")
public record AppProperties(

        @NotBlank
        String owner,

        @NotBlank
        String group,

        @Valid
        Mail mail

) {

    public record Mail(

            @NotBlank
            @Email
            String from,

            @Min(1)
            @Max(10)
            int retryCount,

            Duration timeout,

            boolean enabled

    ) {}
}