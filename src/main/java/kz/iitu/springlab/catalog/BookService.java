package kz.iitu.springlab.catalog;

import java.util.List;
import java.util.Locale;
import kz.iitu.springlab.service.DuplicateTitleException;
import org.springframework.security.access.prepost.PreAuthorize;
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

    @PreAuthorize("hasRole('ADMIN')")
    public Book create(Book book) {
        rejectDuplicate(book, null);
        return repository.create(book);
    }

    @PreAuthorize("hasRole('ADMIN')")
    public Book update(long id, Book book) {
        Book current = findById(id);
        rejectDuplicate(book, id);
        Book replacement = new Book(id, book.title(), book.author(), book.year(), book.genre(),
                current.available(), current.createdAt());
        return repository.replace(id, replacement)
                .orElseThrow(() -> new BookNotFoundException(id));
    }

    @PreAuthorize("hasRole('ADMIN')")
    public Book replace(long id, Book book) {
        return update(id, book);
    }

    @PreAuthorize("hasRole('ADMIN')")
    public void delete(long id) {
        if (!repository.deleteById(id)) {
            throw new BookNotFoundException(id);
        }
    }

    private void rejectDuplicate(Book candidate, Long ignoredId) {
        boolean duplicate = repository.findAll().stream()
                .filter(book -> ignoredId == null || !book.id().equals(ignoredId))
                .anyMatch(book -> sameText(book.title(), candidate.title())
                        && sameText(book.author(), candidate.author()));
        if (duplicate) {
            throw new DuplicateTitleException(candidate.title());
        }
    }

    private boolean sameText(String left, String right) {
        return left != null && right != null && left.trim().equalsIgnoreCase(right.trim());
    }
}
