package kz.iitu.springlab.catalog;

import kz.iitu.springlab.web.Genre;

public record Book(Long id, String title, String author, int year,
                   Genre genre, boolean available) {
    public Book(Long id, String title, String author, int year) {
        this(id, title, author, year, Genre.TECHNOLOGY, true);
    }
}
