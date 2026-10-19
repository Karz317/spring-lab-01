package kz.iitu.springlab;

import java.util.Map;
import kz.iitu.springlab.catalog.Book;
import kz.iitu.springlab.catalog.BookRepository;
import kz.iitu.springlab.web.Genre;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class BookWorkflowTests {
    @Autowired MockMvc mvc;
    @Autowired BookRepository repository;

    @Test
    void formHasFieldsAndAllGenres() throws Exception {
        mvc.perform(get("/books/new"))
                .andExpect(status().isOk()).andExpect(view().name("books/form"))
                .andExpect(model().attributeExists("form", "genres"))
                .andExpect(content().string(containsString("name=\"available\"")))
                .andExpect(content().string(containsString("value=\"HISTORY\"")));
    }

    @ParameterizedTest
    @CsvSource({"title,EMPTY", "title,BLANK", "title,LONG", "author,EMPTY", "author,DIGITS",
                "year,1200", "year,2101", "year,EMPTY", "year,abc", "genre,EMPTY", "genre,UNKNOWN"})
    void invalidFormKeepsValuesAndDoesNotSave(String field, String value) throws Exception {
        int before = repository.findAll().size();
        var params = new java.util.HashMap<>(Map.of("title", "Retained title", "author", "Joshua Bloch",
                "year", "2018", "genre", "TECHNOLOGY", "available", "true"));
        params.put(field, switch(value) {
            case "EMPTY" -> "";
            case "BLANK" -> "   ";
            case "LONG" -> "x".repeat(121);
            case "DIGITS" -> "Bloch 2018";
            default -> value;
        });
        var request = post("/books");
        params.forEach(request::param);
        mvc.perform(request).andExpect(status().isOk()).andExpect(view().name("books/form"))
                .andExpect(model().attributeHasFieldErrors("form", field))
                .andExpect(model().attributeExists("genres"))
                .andExpect(content().string(containsString("is-invalid")))
                .andExpect(content().string(containsString("value=\"" + params.get("title") + "\"")));
        assertThat(repository.findAll()).hasSize(before);
    }

    @ParameterizedTest
    @CsvSource({"1450,false", "2100,true"})
    void validFormPersistsAllFieldsAndFlashIsConsumed(int year, boolean available) throws Exception {
        int before = repository.findAll().size();
        MockHttpSession session = new MockHttpSession();
        var response = mvc.perform(post("/books").session(session)
                        .param("title", "Boundary book " + year).param("author", "Author")
                        .param("year", String.valueOf(year)).param("genre", "HISTORY")
                        .param("available", String.valueOf(available)).param("id", "999"))
                .andExpect(status().isFound()).andExpect(redirectedUrl("/books"))
                .andExpect(flash().attributeExists("message")).andReturn();
        assertThat(repository.findAll()).hasSize(before + 1);
        Book saved = repository.findAll().getLast();
        assertThat(saved.genre()).isEqualTo(Genre.HISTORY);
        assertThat(saved.available()).isEqualTo(available);
        assertThat(saved.id()).isNotEqualTo(999L);
        String message = (String) response.getFlashMap().get("message");
        mvc.perform(get("/books").session(session)).andExpect(content().string(containsString(message)));
        mvc.perform(get("/books").session(session)).andExpect(content().string(not(containsString(message))));
        assertThat(repository.findAll()).hasSize(before + 1);
    }

    @Test
    void russianLocalePersistsAndLocalizesValidationAndFlash() throws Exception {
        MockHttpSession session = new MockHttpSession();
        mvc.perform(get("/books/new").param("lang", "ru").session(session))
                .andExpect(content().string(containsString("Новая книга")))
                .andExpect(content().string(containsString("Технологии")));
        mvc.perform(post("/books").session(session).param("title", "").param("author", "Bloch 2018")
                        .param("year", "abc").param("genre", ""))
                .andExpect(content().string(containsString("Название не может быть пустым")))
                .andExpect(content().string(containsString("Имя автора не должно содержать цифры")))
                .andExpect(content().string(containsString("Введите целое число")))
                .andExpect(content().string(containsString("Выберите жанр")));
        mvc.perform(post("/books").session(session).param("title", "Русская книга").param("author", "Автор")
                        .param("year", "2020").param("genre", "FICTION"))
                .andExpect(flash().attribute("message", "Книга «Русская книга» добавлена"));
        mvc.perform(get("/books/new").param("lang", "en").session(session))
                .andExpect(content().string(containsString("New book")));
    }

    @Test
    void separateNotFoundHandlersReturnHtmlAndProblemJson() throws Exception {
        mvc.perform(get("/books/999"))
                .andExpect(status().isNotFound()).andExpect(content().contentTypeCompatibleWith(MediaType.TEXT_HTML))
                .andExpect(view().name("error/not-found"));
        mvc.perform(get("/api/books/999"))
                .andExpect(status().isNotFound()).andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON))
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.detail").value("Book with id 999 was not found"));
    }

    @ParameterizedTest
    @CsvSource({"0,400", "1,400", "2,200", "60,200", "61,400"})
    void variant12ChecksQueryLengthBoundaries(int length, int expectedStatus) throws Exception {
        var result = mvc.perform(get("/api/books/search").param("q", "x".repeat(length)))
                .andExpect(status().is(expectedStatus));
        if (expectedStatus == 400) {
            result.andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON))
                    .andExpect(jsonPath("$.exception").value("HandlerMethodValidationException"))
                    .andExpect(jsonPath("$.errors[0].parameter").value("q"));
        } else {
            result.andExpect(content().json("[]"));
        }
    }

    @Test
    void variant12SearchIsCaseInsensitiveAndRussianErrorsAreLocalized() throws Exception {
        mvc.perform(get("/api/books/search").param("q", "eFfEcTiVe"))
                .andExpect(status().isOk()).andExpect(jsonPath("$[0].title").value("Effective Java"));
        mvc.perform(get("/api/books/search"))
                .andExpect(status().isBadRequest()).andExpect(jsonPath("$.exception").value("HandlerMethodValidationException"));
        mvc.perform(get("/api/books/search").param("q", "a").param("lang", "ru"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors[0].message").value("Поисковый запрос должен содержать от 2 до 60 символов"));
    }

    @Test
    void previousLabRestCrudFilterAndStaticResourcesWork() throws Exception {
        mvc.perform(get("/api/books").param("author", "Bloch").param("limit", "1"))
                .andExpect(status().isOk()).andExpect(jsonPath("$[0].author").value("Joshua Bloch"));
        mvc.perform(get("/books").param("author", "Bloch"))
                .andExpect(content().string(containsString("Effective Java")))
                .andExpect(content().string(not(containsString("Clean Code"))));
        String result = mvc.perform(post("/api/books").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":999,\"title\":\"REST book\",\"author\":\"Author\","
                                + "\"year\":2020,\"genre\":\"TECHNOLOGY\"}"))
                .andExpect(status().isCreated()).andExpect(header().exists("Location"))
                .andReturn().getResponse().getHeader("Location");
        assertThat(result).isNotEqualTo("/api/books/999");
        mvc.perform(get(result)).andExpect(status().isOk()).andExpect(jsonPath("$.title").value("REST book"));
        mvc.perform(put(result).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"Replaced\",\"author\":\"Author\","
                                + "\"year\":2021,\"genre\":\"SCIENCE\"}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.title").value("Replaced"));
        mvc.perform(delete(result)).andExpect(status().isNoContent()).andExpect(content().string(""));
        mvc.perform(delete(result)).andExpect(status().isNotFound());
        mvc.perform(put("/api/books/999").contentType(MediaType.APPLICATION_JSON)
                .content("{\"title\":\"Missing\",\"author\":\"Author\","
                        + "\"year\":2021,\"genre\":\"SCIENCE\"}"))
                .andExpect(status().isNotFound());
        mvc.perform(get("/css/app.css")).andExpect(status().isOk())
                .andExpect(content().string(containsString(".is-invalid")));
        mvc.perform(get("/")).andExpect(status().isOk()).andExpect(forwardedUrl("index.html"));
        mvc.perform(get("/index.html")).andExpect(status().isOk())
                .andExpect(content().string(containsString("Open catalogue")));
    }

    @Test
    void previousLabErrorStatusesArePreserved() throws Exception {
        mvc.perform(get("/api/books/abc")).andExpect(status().isBadRequest());
        mvc.perform(get("/api/nothing")).andExpect(status().isNotFound());
        mvc.perform(delete("/api/books")).andExpect(status().isMethodNotAllowed());
        mvc.perform(post("/api/books").contentType(MediaType.TEXT_PLAIN).content("hello"))
                .andExpect(status().isUnsupportedMediaType());
        mvc.perform(get("/api/books").accept(MediaType.APPLICATION_XML))
                .andExpect(status().isNotAcceptable());
        mvc.perform(post("/api/books").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"\",\"author\":\"Author\","
                                + "\"year\":2020,\"genre\":\"SCIENCE\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON))
                .andExpect(jsonPath("$.errors[0].field").value("title"));
    }

    @Test
    void duplicateBookReturns409ProblemDetail() throws Exception {
        mvc.perform(post("/api/books").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"Effective Java\",\"author\":\"Joshua Bloch\","
                                + "\"year\":2018,\"genre\":\"TECHNOLOGY\"}"))
                .andExpect(status().isConflict())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON))
                .andExpect(jsonPath("$.title").value("Duplicate title"))
                .andExpect(jsonPath("$.conflictingTitle").value("Effective Java"));
    }

    @Test
    void submittedHtmlIsEscapedInRedisplayedForm() throws Exception {
        mvc.perform(post("/books").param("title", "<script>alert(1)</script>")
                        .param("author", "").param("year", "2020").param("genre", "SCIENCE"))
                .andExpect(content().string(containsString("&lt;script&gt;")))
                .andExpect(content().string(not(containsString("<script>alert(1)</script>"))));
    }
}
