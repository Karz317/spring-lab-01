package kz.iitu.springlab.variant;

import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

@Aspect
@Component
@Order(4)
public class ExceptionTranslationAspect {

    private static final Logger log = LoggerFactory.getLogger(ExceptionTranslationAspect.class);

    @AfterThrowing(pointcut = "@annotation(translate)", throwing = "exception")
    public void recordTechnicalException(
            JoinPoint joinPoint,
            TranslateTechnicalException translate,
            RuntimeException exception) {
        log.error("[TRANSLATE] Technical failure in {}: {}",
                joinPoint.getSignature().toShortString(), exception.getMessage());
    }

    @Around("@annotation(translate)")
    public Object translate(
            ProceedingJoinPoint joinPoint,
            TranslateTechnicalException translate) throws Throwable {
        try {
            return joinPoint.proceed();
        } catch (CatalogException exception) {
            throw exception;
        } catch (RuntimeException exception) {
            throw new CatalogException(
                    "Catalog operation failed: " + joinPoint.getSignature().getName(),
                    exception);
        }
    }
}
