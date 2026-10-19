package kz.iitu.springlab.web.dto;

import java.time.Instant;
import kz.iitu.springlab.web.Genre;

public record BookResponse(
        Long id,
        String title,
        String author,
        int year,
        Genre genre,
        Instant createdAt) {
}
