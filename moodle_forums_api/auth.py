from bs4 import BeautifulSoup

from .http_client import client
from .exceptions import MoodleForumsLoginError, MoodleForumsParseError


def login(username: str, password: str) -> None:
    login_page_res = client.get().get(
        "https://moodle.umontpellier.fr/login/index.php?authCAS=CAS",
    )

    if login_page_res.url.host == "moodle.umontpellier.fr":
        print("Already logged in.")
        return

    login_page = BeautifulSoup(login_page_res.text, "html.parser")

    execution_value = None
    for input_tag in login_page.find_all("input"):
        if input_tag.get("name") == "execution":
            execution_value = input_tag
            break

    if not execution_value or not execution_value.get("value"):
        raise MoodleForumsParseError("Could not find execution value on login page.")

    response = client.get().post(
        login_page_res.url,
        data={
            "username": username,
            "password": password,
            "execution": execution_value["value"],
            "_eventId": "submit",
            "geolocation": "",
            "deviceFingerprint": "1234567890",
        },
    )

    if response.status_code == 401:
        raise MoodleForumsLoginError("Invalid username or password.")
