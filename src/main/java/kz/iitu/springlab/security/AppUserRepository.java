package kz.iitu.springlab.security;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AppUserRepository extends JpaRepository<AppUser, Long> {
    @EntityGraph(attributePaths = "roles")
    Optional<AppUser> findByUsername(String username);

    @EntityGraph(attributePaths = "roles")
    List<AppUser> findAllByOrderByUsernameAsc();
}
