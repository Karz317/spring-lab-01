package kz.iitu.springlab.web;

import java.util.Locale;
import java.util.Map;
import kz.iitu.springlab.catalog.BookNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.MessageSource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.method.annotation.HandlerMethodValidationException;

@RestControllerAdvice(assignableTypes = BookRestController.class)
public class ApiExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(ApiExceptionHandler.class);
    private final MessageSource messages;

    public ApiExceptionHandler(MessageSource messages) {
        this.messages = messages;
    }

    @ExceptionHandler(BookNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ProblemDetail handleNotFound(BookNotFoundException exception, Locale locale) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND,
                messages.getMessage("book.notfound", new Object[]{exception.getId()}, locale));
        problem.setTitle(messages.getMessage("error.notfound", null, locale));
        return problem;
    }

    @ExceptionHandler(HandlerMethodValidationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleMethodValidation(HandlerMethodValidationException exception,
                                               Locale locale) {
        log.info("Handled {} in book search", exception.getClass().getSimpleName());
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST,
                messages.getMessage("book.search.size", null, locale));
        problem.setTitle(messages.getMessage("error.validation", null, locale));
        problem.setProperty("exception", exception.getClass().getSimpleName());
        problem.setProperty("errors", exception.getParameterValidationResults().stream()
                .flatMap(result -> result.getResolvableErrors().stream().map(error -> Map.of(
                        "parameter", result.getMethodParameter().getParameterName(),
                        "message", messages.getMessage(error, locale))))
                .toList());
        return problem;
    }
}
