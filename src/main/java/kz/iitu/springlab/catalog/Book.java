package kz.iitu.springlab.catalog;

import java.time.Instant;
import kz.iitu.springlab.web.Genre;

public record Book(Long id, String title, String author, int year,
                   Genre genre, boolean available, Instant createdAt) {
    public Book(Long id, String title, String author, int year) {
        this(id, title, author, year, Genre.TECHNOLOGY, true, Instant.now());
    }

    public Book(Long id, String title, String author, int year,
                Genre genre, boolean available) {
        this(id, title, author, year, genre, available, Instant.now());
    }
}
