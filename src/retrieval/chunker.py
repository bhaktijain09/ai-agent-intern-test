from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    filename: str
    heading: str
    metadata: dict


def chunk_document(document):

    chunks = []

    current_heading = document.title
    current_text = []

    for line in document.content.splitlines():

        if line.startswith("#"):
            if current_text:
                joined = "\n".join(current_text).strip()

                if joined:
                    chunks.append(
                        Chunk(
                            text=joined,
                            filename=document.filename,
                            heading=current_heading,
                            metadata=document.metadata
                        )
                    )

            current_heading = line.lstrip("#").strip()
            current_text = []

        else:
            current_text.append(line)

    if current_text:
        joined = "\n".join(current_text).strip()

        if joined:
            chunks.append(
                Chunk(
                    text=joined,
                    filename=document.filename,
                    heading=current_heading,
                    metadata=document.metadata
                )
            )

    return chunks


def chunk_documents(documents):

    all_chunks = []

    for document in documents:
        all_chunks.extend(chunk_document(document))

    return all_chunks
