import pytest

from src.retrieval.retriever import Retriever


@pytest.fixture(scope="module")
def retriever():
    return Retriever()


def test_returns_current_policy(retriever):

    retrieval = retriever.retrieve(
        "How long does a regular customer have to return an unused backpack?"
    )

    filenames = [r["filename"] for r in retrieval["results"]]

    assert "01-returns-policy-current.md" in filenames


def test_current_ranks_above_legacy_for_same_topic(retriever):

    retrieval = retriever.retrieve(
        "What is your shipping policy?"
    )

    filenames = [r["filename"] for r in retrieval["results"]]

    if (
        "03-shipping-policy-current.md" in filenames
        and "04-shipping-policy-legacy.md" in filenames
    ):
        current_index = filenames.index("03-shipping-policy-current.md")
        legacy_index = filenames.index("04-shipping-policy-legacy.md")

        assert current_index < legacy_index


def test_internal_docs_never_outrank_current_docs(retriever):

    retrieval = retriever.retrieve(
        "Tell me about the internal content migration notes for the tumbler."
    )

    results = retrieval["results"]

    internal_ranks = [
        i for i, r in enumerate(results) if r["authority"] == "internal"
    ]
    current_ranks = [
        i for i, r in enumerate(results) if r["authority"] == "current"
    ]

    if internal_ranks and current_ranks:
        assert min(current_ranks) < min(internal_ranks)


def test_conflict_detected_for_tumbler_care(retriever):

    retrieval = retriever.retrieve(
        "Is the Breeze Tumbler dishwasher safe?"
    )

    conflict = retrieval["conflict"]

    assert conflict["possible_conflict"] is True
    assert "11-product-care.md" in conflict["sources"]
    assert "12-breeze-tumbler-product-card.md" in conflict["sources"]


def test_no_conflict_for_unambiguous_query(retriever):

    retrieval = retriever.retrieve(
        "Do you offer gift wrapping?"
    )

    conflict = retrieval["conflict"]

    assert conflict["possible_conflict"] is False


def test_authority_classification_uses_frontmatter_not_just_filename(retriever):

    # 11-product-care.md and 12-breeze-tumbler-product-card.md don't have
    # "current" in their filenames, but their frontmatter marks them
    # current, and classification must respect that.
    care_chunks = [
        c for c in retriever.chunks if c.filename == "11-product-care.md"
    ]

    assert care_chunks
    assert retriever.classify_authority(
        care_chunks[0].filename,
        care_chunks[0].metadata
    ) == "current"
