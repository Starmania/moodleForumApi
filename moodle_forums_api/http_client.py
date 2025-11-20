from http import cookiejar

from contextvars import ContextVar

from httpx import Client


current_http_client: ContextVar[Client] = ContextVar(
    "current_http_client",
    default=Client(
        follow_redirects=True,
        timeout=10,
        cookies=cookiejar.MozillaCookieJar(),
    ),
)

client = current_http_client
