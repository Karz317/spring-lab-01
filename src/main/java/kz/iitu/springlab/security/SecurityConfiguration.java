package kz.iitu.springlab.security;

import jakarta.servlet.DispatcherType;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfiguration {
    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
                    .dispatcherTypeMatchers(DispatcherType.ERROR).permitAll()
                    .requestMatchers(HttpMethod.GET, "/", "/index.html", "/css/**").permitAll()
                    .requestMatchers("/admin/**", "/books/new").hasRole("ADMIN")
                    .requestMatchers(HttpMethod.GET, "/books/**", "/api/books/**")
                        .hasAnyRole("USER", "ADMIN")
                    .requestMatchers("/books/**", "/api/books/**").hasRole("ADMIN")
                    .anyRequest().denyAll())
                .formLogin(form -> form.permitAll())
                .logout(logout -> logout.logoutSuccessUrl("/?logout"))
                .csrf(Customizer.withDefaults());
        return http.build();
    }

    @Bean
    PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
