class BaseAPIException(Exception):
    def __init__(self, message: str):
        self.error_code = 400
        self.message = message
        super().__init__(message)