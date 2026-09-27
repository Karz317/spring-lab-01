package kz.iitu.springlab.aspect;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

@Aspect
@Component
@Order(3)
public class TimingAspect {

    private static final Logger log = LoggerFactory.getLogger(TimingAspect.class);
    private static final long SLOW_METHOD_THRESHOLD_MS = 200;

    @Around("kz.iitu.springlab.aspect.Pointcuts.serviceOperation()")
    public Object measure(ProceedingJoinPoint joinPoint) throws Throwable {
        long started = System.nanoTime();
        try {
            return joinPoint.proceed();
        } finally {
            long elapsedMs = (System.nanoTime() - started) / 1_000_000;
            String methodName = joinPoint.getSignature().toShortString();
            if (elapsedMs > SLOW_METHOD_THRESHOLD_MS) {
                log.warn("[TIME] SLOW: {} - {} ms", methodName, elapsedMs);
            } else {
                log.info("[TIME] {} - {} ms", methodName, elapsedMs);
            }
        }
    }
}
