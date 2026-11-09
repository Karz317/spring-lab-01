package kz.iitu.springlab;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.security.test.context.support.WithAnonymousUser;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@WithMockUser(roles = "USER")
class Variant12SecurityTests {
    @Autowired MockMvc mvc;

    @Test
    @WithAnonymousUser
    void anonymousIsRedirectedToLogin() throws Exception {
        mvc.perform(get("/admin"))
                .andExpect(status().isFound()).andExpect(redirectedUrl("/login"));
    }

    @Test
    @WithMockUser(roles = "USER")
    void userIsForbidden() throws Exception {
        mvc.perform(get("/admin")).andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(roles = {"USER", "ADMIN"})
    void adminCanReadTheUserList() throws Exception {
        mvc.perform(get("/admin")).andExpect(status().isOk())
                .andExpect(content().string(containsString("User accounts")))
                .andExpect(content().string(containsString("admin")));
    }
}
