import json
from pathlib import Path
from shutil import rmtree

from moodle_forums_api import login, get_forum
from moodle_forums_api.http_client import client


def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    if Path("cookies.json").exists() and config.get("save_cookies"):
        client.get().cookies.jar.load("cookies.txt", ignore_discard=True)

    login(config["username"], config["password"])

    if config.get("save_cookies"):
        client.get().cookies.jar.save("cookies.txt", ignore_discard=True)

    forum = get_forum(config["forum_id"])

    out = Path(config["output_directory"])
    if out.exists():
        rmtree(out)

    forum.save(out)

    print("Done")


if __name__ == "__main__":
    main()
