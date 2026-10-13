package kz.iitu.springlab.web;

import java.util.Locale;
import kz.iitu.springlab.catalog.BookNotFoundException;
import org.springframework.context.MessageSource;
import org.springframework.http.HttpStatus;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@ControllerAdvice(assignableTypes = BookPageController.class)
public class PageExceptionHandler {
    private final MessageSource messages;

    public PageExceptionHandler(MessageSource messages) {
        this.messages = messages;
    }

    @ExceptionHandler(BookNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public String handleNotFound(BookNotFoundException exception, Model model, Locale locale) {
        model.addAttribute("message", messages.getMessage("book.notfound",
                new Object[]{exception.getId()}, locale));
        return "error/not-found";
    }
}
