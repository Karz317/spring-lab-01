package kz.iitu.springlab.catalog;

import java.util.List;
import java.util.Locale;
import org.springframework.stereotype.Service;

@Service
public class BookService {
    private final BookRepository repository;

    public BookService(BookRepository repository) {
        this.repository = repository;
    }

    public List<Book> findAll(String author) {
        return repository.findAll().stream()
                .filter(book -> author == null || book.author().toLowerCase(Locale.ROOT)
                        .contains(author.toLowerCase(Locale.ROOT)))
                .toList();
    }

    public List<Book> search(String query) {
        String fragment = query.toLowerCase(Locale.ROOT);
        return repository.findAll().stream()
                .filter(book -> book.title().toLowerCase(Locale.ROOT).contains(fragment)).toList();
    }

    public Book findById(long id) {
        return repository.findById(id).orElseThrow(() -> new BookNotFoundException(id));
    }

    public Book create(Book book) {
        return repository.create(book);
    }

    public Book replace(long id, Book book) {
        return repository.replace(id, book).orElseThrow(() -> new BookNotFoundException(id));
    }

    public void delete(long id) {
        if (!repository.deleteById(id)) {
            throw new BookNotFoundException(id);
        }
    }
}
