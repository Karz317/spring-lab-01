package kz.iitu.springlab;

import kz.iitu.springlab.web.validation.NoDigitsValidator;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import static org.assertj.core.api.Assertions.assertThat;

class NoDigitsValidatorTests {
    @ParameterizedTest
    @CsvSource(value = {"NULL,true", "'',true", "Joshua Bloch,true", "Bloch 2018,false", "Автор ٢,false", "Автор 𝟙,false"}, nullValues = "NULL")
    void recognizesUnicodeDigitsButLeavesMissingValuesToNotBlank(String value, boolean expected) {
        assertThat(new NoDigitsValidator().isValid(value, null)).isEqualTo(expected);
    }
}
