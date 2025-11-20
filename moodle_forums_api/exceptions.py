class BaseMoodleForumsAPIException(Exception):
    """Base exception for Moodle Forums API errors."""

    pass


class MoodleForumsAPIConnectionError(BaseMoodleForumsAPIException):
    """Exception raised for connection errors to the Moodle Forums API."""


class MoodleForumsAPIResponseError(BaseMoodleForumsAPIException):
    """Exception raised for invalid responses from the Moodle Forums API."""


class MoodleForumsLoginError(BaseMoodleForumsAPIException):
    """Exception raised for login failures to the Moodle Forums API."""


class MoodleForumsParseError(BaseMoodleForumsAPIException):
    """Exception raised for errors while parsing data from the Moodle Forums Pages."""


class MoodleForumsNotLoggedInError(BaseMoodleForumsAPIException):
    """Exception raised when an action requires authentication but the user is not logged in."""
