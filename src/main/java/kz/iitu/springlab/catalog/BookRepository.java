package kz.iitu.springlab.catalog;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.stereotype.Repository;

@Repository
public class BookRepository {
    private final ConcurrentHashMap<Long, Book> storage = new ConcurrentHashMap<>();
    private final AtomicLong sequence = new AtomicLong();

    public BookRepository() {
        create(new Book(null, "Effective Java", "Joshua Bloch", 2018));
        create(new Book(null, "Clean Code", "Robert Martin", 2008));
        create(new Book(null, "Spring in Action", "Craig Walls", 2022));
    }

    public List<Book> findAll() {
        return storage.values().stream().sorted(Comparator.comparing(Book::id)).toList();
    }

    public Optional<Book> findById(long id) {
        return Optional.ofNullable(storage.get(id));
    }

    public Book create(Book book) {
        long id = sequence.incrementAndGet();
        Book saved = withId(id, book);
        storage.put(id, saved);
        return saved;
    }

    public Optional<Book> replace(long id, Book book) {
        return Optional.ofNullable(storage.computeIfPresent(id, (_, _) -> withId(id, book)));
    }

    public boolean deleteById(long id) {
        return storage.remove(id) != null;
    }

    private Book withId(long id, Book book) {
        return new Book(id, book.title(), book.author(), book.year(), book.genre(), book.available());
    }
}
