class HireMeError(Exception):
    code = "HIREME_ERROR"

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(HireMeError):
    code = "VALIDATION_ERROR"


class UnsafeURLError(HireMeError):
    code = "UNSAFE_URL"


class UnsupportedClaimError(HireMeError):
    code = "UNSUPPORTED_CLAIM"
