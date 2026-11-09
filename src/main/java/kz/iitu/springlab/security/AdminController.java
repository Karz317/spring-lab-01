package kz.iitu.springlab.security;

import java.util.List;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class AdminController {
    private final AppUserRepository users;

    public AdminController(AppUserRepository users) {
        this.users = users;
    }

    @GetMapping("/admin")
    String index(Model model) {
        model.addAttribute("users", users.findAllByOrderByUsernameAsc().stream()
                .map(u -> new UserRow(u.getUsername(), u.isEnabled(), u.getRoles().stream().sorted().toList()))
                .toList());
        return "admin/index";
    }

    public record UserRow(String username, boolean enabled, List<String> roles) {}
}
