package kz.iitu.springlab.web.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import kz.iitu.springlab.web.Genre;
import kz.iitu.springlab.web.validation.NoDigits;

public record BookRequest(
        @NotBlank(message = "{book.title.required}")
        @Size(max = 120, message = "{book.title.size}")
        String title,

        @NotBlank(message = "{book.author.required}")
        @NoDigits
        String author,

        @Min(value = 1450, message = "{book.year.range}")
        @Max(value = 2100, message = "{book.year.range}")
        int year,

        @NotNull(message = "{book.genre.required}")
        Genre genre) {
}
