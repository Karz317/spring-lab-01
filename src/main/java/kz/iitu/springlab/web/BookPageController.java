package kz.iitu.springlab.web;

import jakarta.validation.Valid;
import java.util.Locale;
import kz.iitu.springlab.catalog.Book;
import kz.iitu.springlab.catalog.BookService;
import org.springframework.context.MessageSource;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/books")
public class BookPageController {
    private final BookService service;
    private final MessageSource messages;

    public BookPageController(BookService service, MessageSource messages) {
        this.service = service;
        this.messages = messages;
    }

    @InitBinder("form")
    public void configureBinding(WebDataBinder binder) {
        binder.setAllowedFields("title", "author", "year", "genre", "available");
    }

    @GetMapping
    public String list(@RequestParam(required = false) String author, Model model) {
        model.addAttribute("books", service.findAll(author));
        model.addAttribute("author", author);
        return "books/list";
    }

    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("form", new BookForm());
        model.addAttribute("genres", Genre.values());
        return "books/form";
    }

    @GetMapping("/{id}")
    public String detail(@PathVariable long id, Model model) {
        model.addAttribute("book", service.findById(id));
        return "books/detail";
    }

    @PostMapping
    public String create(@Valid @ModelAttribute("form") BookForm form,
                         BindingResult binding, Model model,
                         RedirectAttributes redirect, Locale locale) {
        if (binding.hasErrors()) {
            model.addAttribute("genres", Genre.values());
            return "books/form";
        }
        Book saved = service.create(new Book(null, form.getTitle(), form.getAuthor(),
                form.getYear(), form.getGenre(), form.isAvailable()));
        redirect.addFlashAttribute("message", messages.getMessage("book.added",
                new Object[]{saved.title()}, locale));
        return "redirect:/books";
    }
}
