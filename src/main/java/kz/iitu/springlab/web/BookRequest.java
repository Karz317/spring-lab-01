package kz.iitu.springlab.web;

import kz.iitu.springlab.catalog.Book;

/** Keeps the lab 5 JSON body compatible while accepting the new optional fields. */
public record BookRequest(String title, String author, int year, Genre genre, Boolean available) {
    public Book toBook() {
        return new Book(null, title, author, year,
                genre == null ? Genre.TECHNOLOGY : genre,
                available == null || available);
    }
}
