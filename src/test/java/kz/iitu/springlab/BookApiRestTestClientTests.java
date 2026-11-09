package kz.iitu.springlab;

import java.net.URI;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.client.RestTestClient;
import org.springframework.web.context.WebApplicationContext;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.setup.MockMvcBuilders.webAppContextSetup;

@SpringBootTest
@ActiveProfiles("test")
@WithMockUser(roles = "ADMIN")
class BookApiRestTestClientTests {
    private RestTestClient client;

    @BeforeEach
    void setUp(WebApplicationContext context) {
        var mvc = webAppContextSetup(context).apply(springSecurity())
                .defaultRequest(get("/").with(csrf())).build();
        client = RestTestClient.bindTo(mvc).build();
    }

    @Test
    void createReturns201AndLocation() {
        String title = "RestTestClient " + UUID.randomUUID();

        var result = client.post().uri("/api/books")
                .contentType(MediaType.APPLICATION_JSON)
                .body(json(title))
                .exchange()
                .expectStatus().isCreated()
                .expectHeader().exists("Location")
                .expectBody()
                .jsonPath("$.title").isEqualTo(title)
                .jsonPath("$.createdAt").exists()
                .returnResult();

        URI location = result.getResponseHeaders().getLocation();
        assertThat(location).isNotNull();
        client.get().uri(location.toString())
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.title").isEqualTo(title);
    }

    @Test
    void missingBookReturns404ProblemDetail() {
        client.get().uri("/api/books/999999")
                .accept(MediaType.APPLICATION_PROBLEM_JSON)
                .exchange()
                .expectStatus().isNotFound()
                .expectHeader().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON)
                .expectBody()
                .jsonPath("$.status").isEqualTo(404)
                .jsonPath("$.title").isEqualTo("Book not found")
                .jsonPath("$.instance").isEqualTo("/api/books/999999");
    }

    @Test
    void deleteReturns204AndNoBody() {
        var created = client.post().uri("/api/books")
                .contentType(MediaType.APPLICATION_JSON)
                .body(json("Delete " + UUID.randomUUID()))
                .exchange()
                .expectStatus().isCreated()
                .expectBody()
                .returnResult();
        URI location = created.getResponseHeaders().getLocation();
        assertThat(location).isNotNull();

        client.delete().uri(location.toString())
                .exchange()
                .expectStatus().isNoContent()
                .expectBody().isEmpty();
    }

    private String json(String title) {
        return """
                {
                  "title": "%s",
                  "author": "Test Author",
                  "year": 2026,
                  "genre": "TECHNOLOGY"
                }
                """.formatted(title);
    }
}
