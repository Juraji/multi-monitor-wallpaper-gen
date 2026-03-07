from textual.validation import Validator, ValidationResult, Failure


class EndsWith(Validator):
    class InputEmpty(Failure):
        """Indicates that the value is empty."""

    class DoesNotEndWith(Failure):
        """Indicates that the value does not end with a valid string."""

    def __init__(self, expected: str | list[str]):
        super().__init__()
        self.expectations = expected if isinstance(expected, list) else [expected]

    def validate(self, value: str) -> ValidationResult:
        if len(value) == 0:
            return ValidationResult.failure([self.InputEmpty(self, value)])

        for expectation in self.expectations:
            if value.endswith(expectation):
                return self.success()

        return ValidationResult.failure([self.DoesNotEndWith(self, value)])

    def describe_failure(self, failure: Failure) -> str | None:
        match failure:
            case self.InputEmpty:
                return f'Input is empty, but it should end with on of {self.expectations}.'
            case self.DoesNotEndWith:
                return f'Input does not end with any of {self.expectations}.'
            case _:
                return None
