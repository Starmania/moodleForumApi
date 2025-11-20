from datetime import datetime
from typing import Optional, no_type_check
from pathlib import Path

from bs4 import BeautifulSoup
from bs4 import Tag
from html_to_markdown import convert

from .http_client import client
from .post import Discussion
from .exceptions import MoodleForumsParseError


class Forum:
    def __init__(self, forum_id: int):
        self.forum_id = forum_id
        self.forum_name: Optional[str] = None
        self.forum_summary: Optional[str] = None
        self.discussions: list[Discussion] = []
        self.path: Optional[tuple[tuple[str, str], ...]] = None
        self.accessible = False

    def setup(self):
        # https://moodle.umontpellier.fr/mod/forum/view.php?id=1016665
        initial_page_response = client.get().get(
            f"https://moodle.umontpellier.fr/mod/forum/view.php?id={self.forum_id}",
            follow_redirects=False,
        )

        initial_page = BeautifulSoup(initial_page_response.text, "html.parser")

        if initial_page_response.status_code != 200:
            return

        self.accessible = True
        self.path = tuple(
            (str(a_tag.text).replace("\n", "").strip(), str(a_tag["href"]))
            for a_tag in initial_page.find("div", id="page-navbar").find_all("a")
        )
        self.forum_name = initial_page.find("h1", class_="h2").text.strip()
        self.forum_summary = convert(str(initial_page.find("div", id="intro"))).strip()

        self.update_discussions()

    def __repr__(self):
        return f"<Forum id={self.forum_id} name={self.forum_name} posts_count={len(self.discussions)} path={self.path}>"

    def update_discussions(self):
        if not self.accessible:
            return

        main_page_response = client.get().get(
            f"https://moodle.umontpellier.fr/mod/forum/view.php?id={self.forum_id}",
        )
        main_page = BeautifulSoup(main_page_response.text, "html.parser")

        seen_discussion_ids = set()

        self._extract_discussions(main_page, seen_discussion_ids)

        for discussion in self.discussions:
            if discussion.discussion_id not in seen_discussion_ids:
                self.discussions.remove(discussion)

    @no_type_check
    def _extract_discussions(self, main_page: Tag, seen_discussion_ids: set[int]):
        try:
            for discussion_row in main_page.find_all("tr", class_="discussion"):
                discussion_id = int(discussion_row.get("data-discussionid", "0"))
                seen_discussion_ids.add(discussion_id)

                discussion = self._get_discussion_by_id(discussion_id)

                if discussion is not None:
                    discussion.update_posts()

                # Favorited
                is_favorited = (
                    discussion_row.find(
                        "a", attrs={"data-type": "favorite-toggle"}
                    ).get("data-targetstate")
                    == "0"
                )

                title: str = (
                    discussion_row.find(
                        "th",
                        class_="topic",
                    )
                    .find("a")
                    .get("title")
                )

                author_and_dt = discussion_row.find("td", class_="author").find(
                    None, class_="author-info"
                )
                author = author_and_dt.findChild().text
                date_timestamp = author_and_dt.find("time")["data-timestamp"]
                created_at = datetime.fromtimestamp(int(date_timestamp))
                is_subscribed = (
                    discussion_row.find(
                        "input", attrs={"data-type": "subscription-toggle"}
                    ).get(  # pyright: ignore[reportOptionalMemberAccess]
                        "data-targetstate"
                    )
                    == "0"
                )

                discussion = Discussion(
                    discussion_id,
                    title,
                    author,
                    created_at,
                    [],
                    is_subscribed,
                    is_favorited,
                )

                discussion.update_posts()

                self.discussions.append(discussion)

        except AttributeError as e:
            raise MoodleForumsParseError from e

    def _get_discussion_by_id(self, discussion_id: int) -> Discussion | None:
        for discussion in self.discussions:
            if discussion.discussion_id == discussion_id:
                return discussion
        return None

    def __iter__(self):
        return iter(self.discussions)

    @staticmethod
    def get_forum(forum_id: int) -> "Forum":
        forum = Forum(forum_id)
        forum.setup()
        return forum

    def save(self, path: Path) -> None:
        """Save the full architecture as .md file

        Args:
            path (Path): folder to use
        """
        if not self.accessible:
            return

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        elif not path.is_dir():
            raise ValueError(f"The path {path} is not a directory.")

        for discussion in self.discussions:
            discussion_path = path / f"{discussion.discussion_id}"
            discussion.save(discussion_path)
