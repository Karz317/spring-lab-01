package kz.iitu.springlab.service;

import java.util.List;
import java.util.stream.IntStream;

import kz.iitu.springlab.audit.Audited;
import kz.iitu.springlab.variant.TranslateTechnicalException;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Service;

@Service
public class CatalogService {

    private final ObjectProvider<CatalogService> selfProvider;

    public CatalogService(ObjectProvider<CatalogService> selfProvider) {
        this.selfProvider = selfProvider;
    }

    public String findById(long id) {
        sleep(50);
        return "Item no. " + id;
    }

    @Audited(action = "CATALOG_LIST", logArguments = true)
    public List<String> findAll(int limit) {
        sleep(300);
        return IntStream.rangeClosed(1, limit)
                .mapToObj(number -> "Item no. " + number)
                .toList();
    }

    @Audited(action = "CATALOG_REMOVE")
    public String remove(long id) {
        if (id <= 0) {
            throw new IllegalArgumentException("Invalid identifier: " + id);
        }
        return "Removed item no. " + id;
    }

    public String removeTwice(long id) {
        String first = remove(id);
        String second = remove(id + 1);
        return first + "; " + second;
    }

    public String removeTwiceFixed(long id) {
        CatalogService proxy = selfProvider.getObject();
        String first = proxy.remove(id);
        String second = proxy.remove(id + 1);
        return first + "; " + second;
    }

    @TranslateTechnicalException
    public String loadFromExternalSystem(long id) {
        throw new IllegalStateException("Database connection is unavailable for item " + id);
    }

    private void sleep(long milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
        }
    }
}
