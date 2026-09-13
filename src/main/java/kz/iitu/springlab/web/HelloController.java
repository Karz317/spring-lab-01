package kz.iitu.springlab.web;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;


import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;

@RestController
@RequestMapping("/api")
public class HelloController {

    @Value("${app.owner:unknown}")
    private String owner;

    @GetMapping("/hello")
    public Greeting hello(@RequestParam(defaultValue = "world") String name) {
        return new Greeting(
                "Hello, " + name + "!",
                owner,
                LocalDateTime.now()
        );
    }

    @GetMapping("/info")
    public Info info() {
        return new Info(
                owner,
                System.getProperty("java.version"),
                Runtime.getRuntime().availableProcessors()
        );
    }

    public record Greeting(
            String message,
            String owner,
            LocalDateTime timestamp
    ) {}

    public record Info(
            String owner,
            String javaVersion,
            int cpuCores
    ) {}

    @GetMapping("/time")
    public TimeInfo time(
            @RequestParam(defaultValue = "Asia/Almaty") String zone) {

        ZoneId zoneId = ZoneId.of(zone);
        ZonedDateTime now = ZonedDateTime.now(zoneId);

        return new TimeInfo(
                zone,
                now.toLocalDateTime(),
                now.getOffset().toString()
        );
    }

    public record TimeInfo(
            String zone,
            LocalDateTime time,
            String utcOffset
    ) {}
}