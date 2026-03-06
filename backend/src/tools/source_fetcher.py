"""Reference source fetching tool."""

import httpx
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from src.core.exceptions import SourceFetchError
from src.models.report import SourceDocument


class SourceFetcherTool:
    """Fetch and normalize reference URLs into plain text documents."""

    async def fetch(self, reference_urls: list[HttpUrl]) -> list[SourceDocument]:
        """Fetch each URL and extract a compact plain text representation."""
        if not reference_urls:
            return []

        results: list[SourceDocument] = []
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            for url in reference_urls:
                try:
                    response = await client.get(str(url))
                    response.raise_for_status()
                except httpx.HTTPError as exc:
                    raise SourceFetchError(f"Failed to fetch source {url}: {exc}") from exc

                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else str(url)
                text_content = " ".join(soup.get_text(separator=" ").split())

                results.append(
                    SourceDocument(
                        url=url,
                        title=title,
                        content=text_content[:8000],
                    )
                )

        return results
