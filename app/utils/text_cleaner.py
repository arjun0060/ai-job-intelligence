from html import unescape
from bs4 import BeautifulSoup


def clean_html(html: str | None) -> str | None:
    if not html:
        return None

    html = unescape(html)

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    text = soup.get_text(
        separator="\n",
        strip=True
    )

    # Remove excessive empty lines
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)