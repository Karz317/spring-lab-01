package kz.iitu.springlab.audit;

import java.time.Instant;
import java.util.Arrays;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

@Aspect
@Component
@Order(1)
public class AuditAspect {

    private static final Logger log = LoggerFactory.getLogger(AuditAspect.class);

    @Around("@annotation(audited)")
    public Object audit(ProceedingJoinPoint joinPoint, Audited audited) throws Throwable {
        if (audited.logArguments()) {
            log.info("[AUDIT] start {} at={} args={}",
                    audited.action(), Instant.now(), Arrays.toString(joinPoint.getArgs()));
        } else {
            log.info("[AUDIT] start {} at={}", audited.action(), Instant.now());
        }

        try {
            Object result = joinPoint.proceed();
            log.info("[AUDIT] {} success", audited.action());
            return result;
        } catch (Throwable exception) {
            log.error("[AUDIT] {} failure: {}", audited.action(), exception.getMessage());
            throw exception;
        }
    }
}
