class AppError(Exception):
    status_code = 400
    message = "Application error"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    message = "Resource not found"


class ValidationError(AppError):
    status_code = 422
    message = "Validation failed"


class ConflictError(AppError):
    status_code = 409
    message = "Conflict"


class ExternalServiceError(AppError):
    status_code = 502
    message = "External service error"
