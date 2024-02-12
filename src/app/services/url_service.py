import string
import uuid
import concurrent
import threading
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from app.utils.snowflake_utils import SnowflakeIDGenerator


class URLShortener:
    def __init__(self):
        self.id_to_url = {}
        self.url_to_id = {}
        self.alphabet = string.digits + string.ascii_letters
        self.base = len(self.alphabet)
        self.lock = threading.Lock()

    @lru_cache(maxsize=1024)
    def encode(self, unique_id: int) -> str:
        if unique_id <= 0:
            raise ValueError("unique_id must be a positive integer")

        parts = []
        while unique_id:
            unique_id, rem = divmod(unique_id, self.base)
            parts.append(self.alphabet[rem])

        return "".join(reversed(parts))

    def add_url(self, long_url: str) -> str:
        with self.lock:
            if not long_url:
                raise ValueError("The input long_url cannot be empty.")

            if long_url in self.url_to_id:
                return f"http://short.url/{self.url_to_id[long_url]}"
            unique_id = uuid.uuid4().int & ((1 << 64) - 1)
            short_path = self.encode(unique_id)
            self.url_to_id[long_url] = short_path
            self.id_to_url[short_path] = long_url

            return f"http://short.url/{short_path}"

    @lru_cache(maxsize=1024)
    def get_long_url(self, short_url: str) -> str | None:
        if not short_url.startswith("http://short.url/"):
            return None

        short_path = short_url.split("/")[-1]

        if not short_path.isalnum():
            return None

        return self.id_to_url.get(short_path)

    def add_urls(self, urls: str | list[str]) -> list[str]:
        if isinstance(urls, str):
            urls = [urls]

        return [self.add_url(url) for url in urls]

    def add_urls_concurrently(self, urls: list[str], max_workers: int = 10) -> list[str]:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.add_url, url): url for url in urls}
            results = []
            for future in concurrent.futures.as_completed(future_to_url):
                results.append(future.result())

            return results


if __name__ == "__main__":
    shortener = URLShortener()
    _long_url = "https://example.bin.com/"
    _short_url = shortener.add_url(_long_url)
    print(f"Short URL: {_short_url}")

    retrieved_long_url = shortener.get_long_url(_short_url)
    print(f"Retrieved Long URL: {retrieved_long_url}")
    print()

    _long_urls = ["https://example.fedora.com/very/long/url",
                  "https://example.fedora.com/very2/long/url",
                  "https://example.fedora.com/very3/long/url"]
    for _url in shortener.add_urls_concurrently(_long_urls):
        print(f"Short URL: {_url}")
    print()

    _unique_id = uuid.uuid4().int & (1 << 64) - 1
    print(f"unique_id:", _unique_id)
    print(f"Encode base62: {shortener.encode(_unique_id)}")
    print()

    id_generator = SnowflakeIDGenerator(data_center_id=0, worker_id=0)
    distributed_id = id_generator.get_id()
    print(f"Distributed_id:", distributed_id)
    print(f"Encode base62: {shortener.encode(distributed_id)}")
