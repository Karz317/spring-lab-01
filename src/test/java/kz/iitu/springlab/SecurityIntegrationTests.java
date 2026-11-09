package kz.iitu.springlab;

import kz.iitu.springlab.catalog.BookRepository;
import kz.iitu.springlab.catalog.BookService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.assertj.core.api.Assertions.*;
import static org.hamcrest.Matchers.containsString;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestBuilders.formLogin;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.response.SecurityMockMvcResultMatchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class SecurityIntegrationTests {
    @Autowired MockMvc mvc;
    @Autowired JdbcTemplate jdbc;
    @Autowired PasswordEncoder encoder;
    @Autowired BookService books;
    @Autowired BookRepository repository;

    @Test
    void migratedHashesAuthenticateAndDisabledUserIsRejected() throws Exception {
        String hash = jdbc.queryForObject(
                "select password_hash from app_user where username = 'user'", String.class);
        assertThat(hash).hasSize(60).startsWith("$2a$10$");
        assertThat(encoder.matches("user123", hash)).isTrue();
        assertThat(encoder.encode("user123")).isNotEqualTo(hash);

        mvc.perform(formLogin().user("user").password("user123"))
                .andExpect(authenticated().withRoles("USER"));
        mvc.perform(formLogin().user("admin").password("admin123"))
                .andExpect(authenticated().withRoles("ADMIN", "USER"));

        jdbc.update("update app_user set enabled = false where username = 'user'");
        try {
            mvc.perform(formLogin().user("user").password("user123"))
                    .andExpect(unauthenticated()).andExpect(redirectedUrl("/login?error"));
        } finally {
            jdbc.update("update app_user set enabled = true where username = 'user'");
        }
    }

    @Test
    @WithMockUser(roles = "USER")
    void directServiceInvocationCannotDeleteAndWriteRequestIsForbidden() throws Exception {
        assertThatThrownBy(() -> books.delete(1L)).isInstanceOf(AccessDeniedException.class);
        assertThat(repository.findById(1L)).isPresent();
        mvc.perform(post("/books").with(csrf())).andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void missingCsrfCannotMutateAndValidCsrfCan() throws Exception {
        int before = repository.findAll().size();
        mvc.perform(get("/books/new"))
                .andExpect(content().string(containsString("name=\"_csrf\"")));
        mvc.perform(newBook()).andExpect(status().isForbidden());
        assertThat(repository.findAll()).hasSize(before);
        mvc.perform(newBook().with(csrf())).andExpect(redirectedUrl("/books"));
        assertThat(repository.findAll()).hasSize(before + 1);
    }

    private org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder newBook() {
        return post("/books").param("title", "CSRF integration test").param("author", "Lab Author")
                .param("year", "2020").param("genre", "FICTION");
    }
}
