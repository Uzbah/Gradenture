class AppError(Exception):
    """Raised by services; mapped to JSON responses in main.py."""

    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self.body = body
        super().__init__(body)
