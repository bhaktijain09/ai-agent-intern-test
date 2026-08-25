import os
import re
from dataclasses import dataclass


@dataclass
class Document:
    filename: str
    title: str
    metadata: dict
    content: str


def parse_frontmatter(text: str):
    metadata = {}

    if not text.startswith("---"):
        return metadata, text

    parts = text.split("---", 2)

    if len(parts) < 3:
        return metadata, text

    frontmatter = parts[1]
    content = parts[2]

    for line in frontmatter.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata, content.strip()


def load_documents(directory: str):
    documents = []

    for filename in sorted(os.listdir(directory)):

        if not filename.endswith(".md"):
            continue

        path = os.path.join(directory, filename)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        metadata, content = parse_frontmatter(text)

        title_match = re.search(
            r"^#\s+(.+)$",
            content,
            re.MULTILINE
        )

        title = (
            title_match.group(1)
            if title_match
            else filename
        )

        documents.append(
            Document(
                filename=filename,
                title=title,
                metadata=metadata,
                content=content
            )
        )

    return documents
