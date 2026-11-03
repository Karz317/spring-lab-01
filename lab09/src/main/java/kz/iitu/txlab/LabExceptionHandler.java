package kz.iitu.txlab;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.dao.OptimisticLockingFailureException;
@RestControllerAdvice
public class LabExceptionHandler {
    @ExceptionHandler(IllegalArgumentException.class)
    public ProblemDetail invalid(IllegalArgumentException e) { return ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST,e.getMessage()); }
    @ExceptionHandler({IllegalStateException.class, OptimisticLockingFailureException.class})
    public ProblemDetail conflict(RuntimeException e) { return ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT,e.getMessage()); }
}
