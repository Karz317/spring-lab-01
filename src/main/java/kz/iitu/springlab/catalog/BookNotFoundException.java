package kz.iitu.springlab.catalog;

public class BookNotFoundException extends RuntimeException {
    private final long id;

    public BookNotFoundException(long id) {
        super("Book with id " + id + " was not found");
        this.id = id;
    }

    public long getId() {
        return id;
    }
}
