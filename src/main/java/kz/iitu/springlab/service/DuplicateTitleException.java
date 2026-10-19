package kz.iitu.springlab.service;

public class DuplicateTitleException extends RuntimeException {
    private final String title;

    public DuplicateTitleException(String title) {
        super("A book with title '" + title + "' and the same author already exists");
        this.title = title;
    }

    public String getTitle() {
        return title;
    }
}
