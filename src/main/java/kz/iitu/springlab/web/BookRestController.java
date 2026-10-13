package kz.iitu.springlab.web;

import jakarta.validation.constraints.Size;
import java.net.URI;
import java.util.List;
import kz.iitu.springlab.catalog.Book;
import kz.iitu.springlab.catalog.BookService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

@RestController
@RequestMapping("/api/books")
public class BookRestController {
    private final BookService service;

    public BookRestController(BookService service) {
        this.service = service;
    }

    @GetMapping
    public List<Book> list(@RequestParam(required = false) String author,
                           @RequestParam(defaultValue = "10") int limit) {
        if (limit < 0) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "limit must not be negative");
        }
        return service.findAll(author).stream().limit(limit).toList();
    }

    // Spring MVC performs method validation; class-level @Validated is intentionally absent.
    @GetMapping("/search")
    public List<Book> search(@RequestParam(defaultValue = "")
                            @Size(min = 2, max = 60, message = "{book.search.size}") String q) {
        return service.search(q);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Book> find(@PathVariable long id) {
        return ResponseEntity.ok(service.findById(id));
    }

    @PostMapping
    public ResponseEntity<Book> create(@RequestBody BookRequest book) {
        Book saved = service.create(book.toBook());
        return ResponseEntity.created(URI.create("/api/books/" + saved.id())).body(saved);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Book> replace(@PathVariable long id, @RequestBody BookRequest book) {
        return ResponseEntity.ok(service.replace(id, book.toBook()));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
