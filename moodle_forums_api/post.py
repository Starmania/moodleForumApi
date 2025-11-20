import datetime
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from html_to_markdown import convert

from .http_client import client


class Post:
    def __init__(
        self,
        discussion_id: int,
        post_id: int,
        title: str,
        author: str,
        content: str,
        created_at: datetime.datetime,
    ):
        self.discussion_id = discussion_id
        self.post_id = post_id
        self.title = title
        self.author = author
        self.content = content
        self.created_at = created_at
        self.responds_to: "Post | int | None" = None

    def __repr__(self):
        return f"<Post id={self.post_id} discussion_id={self.discussion_id} author={self.author} created_at={self.created_at}>"

    def __str__(self) -> str:
        return "\n".join(
            (
                f"# {self.title}",
                f"par {self.author}, {self.created_at}",
                "-"
                * (
                    max(
                        len(self.title) + 2,
                        3 + len(self.author) + 2 + len(str(self.created_at)),
                    )
                    + 2
                ),
                self.content,
            )
        )


class Discussion:
    def __init__(
        self,
        discussion_id: int,
        title: str,
        author: str,
        created_at: datetime.datetime,
        posts: list[Post],
        is_subscribed: bool = False,
        is_favorited: bool = False,
    ):
        self.discussion_id = discussion_id
        self.title = title
        self.author = author
        self.created_at = created_at
        self.posts = posts
        self.is_subscribed = is_subscribed
        self.is_favorited = is_favorited

    def __repr__(self):
        return f"<Discussion id={self.discussion_id} title={self.title} author={self.author} posts_count={len(self.posts)}>"

    def update_posts(self) -> None:
        discussion_page_response = client.get().get(
            f"https://moodle.umontpellier.fr/mod/forum/discuss.php?mode=3&d={self.discussion_id}",
        )
        discussion_page = BeautifulSoup(discussion_page_response.text, "html.parser")

        seen_post_ids: set[int] = set()

        self._parse_posts(discussion_page, seen_post_ids)

        for post in self.posts:
            if post.post_id not in seen_post_ids:
                self.posts.remove(post)

    def _parse_posts(self, discussion_page: Tag, seen_post_ids: set[int]):
        for post_div in discussion_page.find_all("div", class_="forumpost"):
            post_id = int(post_div.get("data-post-id", "0"))

            seen_post_ids.add(post_id)

            post = self._get_post_by_id(post_id)

            if post is None:
                post = Post(
                    self.discussion_id,
                    post_id,
                    "",
                    "",
                    "",
                    datetime.datetime.now(),
                )
                self.posts.append(post)

            post.title = post_div.find("h3", class_="h6").text.strip()
            author_date_div = post_div.find("h3", class_="h6").find_next_sibling()
            post.author = author_date_div.find("a").text.strip()
            date_str = author_date_div.find("time")["datetime"]
            post.created_at = datetime.datetime.fromisoformat(date_str)
            if post_div.parent.parent.parent.get("data-post-id") != None:
                post.responds_to = int(
                    post_div.parent.parent.parent.get("data-post-id")
                )

            post_content = post_div.find("div", class_="post-content-container")
            post.content = convert(str(post_content)).strip()

    def _get_post_by_id(self, post_id: int) -> "Post | None":
        for post in self.posts:
            if post.post_id == post_id:
                return post
        return None

    def save(self, path: Path) -> None:
        """Save the discussion as a .md file

        Args:
            path (Path): folder to use
        """
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        elif not path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        for post in self.posts:
            post_path = path / f"discussion_{self.discussion_id}_post_{post.post_id}.md"
            with post_path.open("w", encoding="utf-8") as f:
                f.write(str(post))
