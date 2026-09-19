import dataclasses

from enum import Enum


class CustomCodeBase(Enum):
    """Base for the project's response-code enums."""

    @property
    def code(self) -> int:
        """The numeric code carried in the response body."""
        return self.value[0]

    @property
    def msg(self) -> str:
        """The human-readable message carried in the response body."""
        return self.value[1]


class CustomResponseCode(CustomCodeBase):
    """General response codes."""

    HTTP_200 = (200, 'Success')
    HTTP_201 = (201, 'Created')
    HTTP_400 = (400, 'Bad request')
    HTTP_401 = (401, 'Not authenticated')
    HTTP_403 = (403, 'Forbidden')
    HTTP_404 = (404, 'Not found')
    HTTP_405 = (405, 'Method not allowed')
    HTTP_409 = (409, 'Conflict')
    HTTP_413 = (413, 'Payload too large')
    HTTP_422 = (422, 'Validation error')
    HTTP_429 = (429, 'Too many requests')
    HTTP_500 = (500, 'Internal server error')


class CustomErrorCode(CustomCodeBase):
    """Application-specific error codes.

    These are carried in the body's ``code`` field while the HTTP status stays a
    standard one, so the frontend can branch on a precise cause when it needs to.
    """

    TOKEN_EXPIRED = (40101, 'Token expired')
    TOKEN_INVALID = (40102, 'Invalid token')
    ACCOUNT_SUSPENDED = (40301, 'Account suspended')
    EMAIL_NOT_VERIFIED = (40302, 'Email not verified')
    COMPANY_EXISTS = (40901, 'Company already exists')
    EDIT_ALREADY_PENDING = (40902, 'An edit for this company is already pending review')


@dataclasses.dataclass
class CustomResponse:
    """An open-ended code/message pair, for one-off responses that do not warrant an enum member."""

    code: int
    msg: str


class StandardResponseCode:
    """HTTP status codes used by this project.

    See the IANA registry: https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
    """

    HTTP_200 = 200  # OK
    HTTP_201 = 201  # CREATED
    HTTP_204 = 204  # NO_CONTENT
    HTTP_400 = 400  # BAD_REQUEST
    HTTP_401 = 401  # UNAUTHORIZED
    HTTP_403 = 403  # FORBIDDEN
    HTTP_404 = 404  # NOT_FOUND
    HTTP_405 = 405  # METHOD_NOT_ALLOWED
    HTTP_409 = 409  # CONFLICT
    HTTP_413 = 413  # CONTENT_TOO_LARGE
    HTTP_422 = 422  # UNPROCESSABLE_ENTITY
    HTTP_429 = 429  # TOO_MANY_REQUESTS
    HTTP_500 = 500  # INTERNAL_SERVER_ERROR
    HTTP_502 = 502  # BAD_GATEWAY
    HTTP_503 = 503  # SERVICE_UNAVAILABLE
