"""
Builds the retriever's chunk + embedding index once and prints a
summary, so you can sanity-check the knowledge base (chunk counts,
authority classification, source list) before firing up the full
Streamlit app.

The Retriever currently rebuilds its FAISS index in-memory on every
process start (see src/retrieval/retriever.py) since the knowledge
base here is small enough that this takes a couple of seconds, not
minutes. This script exists as a fast feedback loop for iterating on
knowledge-base content, and as a place to add on-disk caching later
if the corpus grows.

Usage:
    python scripts/build_index.py
"""

import os
import sys
from collections import Counter

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from src.retrieval.retriever import Retriever


def main():

    print("Loading documents and building index...")
    retriever = Retriever()

    print(f"\nLoaded {len(retriever.chunks)} chunks.")

    by_authority = Counter()
    by_file = Counter()

    for chunk in retriever.chunks:
        authority = retriever.classify_authority(
            chunk.filename,
            chunk.metadata
        )
        by_authority[authority] += 1
        by_file[chunk.filename] += 1

    print("\nChunks by authority level:")
    for authority, count in sorted(by_authority.items()):
        print(f"  {authority:12s} {count}")

    print("\nChunks by source file:")
    for filename, count in sorted(by_file.items()):
        authority = retriever.classify_authority(
            filename,
            next(
                c.metadata for c in retriever.chunks
                if c.filename == filename
            )
        )
        print(f"  {filename:45s} {count:3d} chunks  [{authority}]")

    print("\nSanity check: known conflict pair")
    retrieval = retriever.retrieve(
        "Is the Breeze Tumbler dishwasher safe or hand wash only?"
    )
    conflict = retrieval["conflict"]
    status = "DETECTED" if conflict["possible_conflict"] else "NOT DETECTED"
    print(f"  Conflict {status}: {conflict['sources']}")

    print("\nIndex build OK.")


if __name__ == "__main__":
    main()
