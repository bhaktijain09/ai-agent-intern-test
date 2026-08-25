"""
Behavioral evaluation runner.

Runs every case in visible-cases.json and custom-cases.json against a
fresh SupportAgent and checks behavioral assertions, not just "did it
respond". Each case can assert on:

  - must_include:      substrings that MUST appear in the final response
  - must_not_include:  substrings that MUST NOT appear in the final response
  - tool:               tool that should have been invoked (order_lookup)
  - source_filename:    a knowledge-base filename that should have been
                         among the retrieved sources for the final turn
  - handoff:            whether the response should read as a human
                         hand-off / "I don't know" / conflict admission
                         (checked heuristically via keywords)

Usage:
    python evaluation/evaluate.py
    python evaluation/evaluate.py --cases custom
"""

import argparse
import json
import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from src.agent import SupportAgent
from src.llm.gemini import GeminiClient
from src.retrieval.retriever import Retriever


HANDOFF_KEYWORDS = [
    "human support",
    "contact support",
    "recommend human",
    "conflict",
    "i don't have information",
    "i can't help with that",
    "i couldn't find",
    "check with human",
]


def load_cases(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def looks_like_handoff(response):
    lowered = response.lower()
    return any(keyword in lowered for keyword in HANDOFF_KEYWORDS)


def run_case(agent, case):

    failures = []
    response = None

    for turn in case["messages"]:
        response = agent.respond(turn["content"])

    expect = case.get("expect", {})
    lowered_response = response.lower()

    for phrase in expect.get("must_include", []):
        if phrase.lower() not in lowered_response:
            failures.append(f"missing required phrase: {phrase!r}")

    for phrase in expect.get("must_not_include", []):
        if phrase.lower() in lowered_response:
            failures.append(f"contains forbidden phrase: {phrase!r}")

    if "tool" in expect:
        called = agent.last_tool_call
        if not called or called.get("tool") != expect["tool"]:
            failures.append(
                f"expected tool {expect['tool']!r}, got {called!r}"
            )

    if "source_filename" in expect:
        retrieval = agent.last_retrieval or {"results": []}
        filenames = [r["filename"] for r in retrieval["results"]]
        if expect["source_filename"] not in filenames:
            failures.append(
                f"expected source {expect['source_filename']!r} in "
                f"retrieved filenames {filenames}"
            )

    if "handoff" in expect:
        is_handoff = looks_like_handoff(response)
        if is_handoff != expect["handoff"]:
            failures.append(
                f"expected handoff={expect['handoff']}, "
                f"response {'looked' if is_handoff else 'did not look'} "
                f"like a handoff"
            )

    return response, failures


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        choices=["visible", "custom", "all"],
        default="all"
    )
    args = parser.parse_args()

    eval_dir = os.path.dirname(os.path.abspath(__file__))

    case_files = []

    if args.cases in ("visible", "all"):
        case_files.append(
            os.path.join(eval_dir, "visible-cases.json")
        )

    if args.cases in ("custom", "all"):
        case_files.append(
            os.path.join(eval_dir, "custom-cases.json")
        )

    cases = []
    for file_path in case_files:
        cases.extend(load_cases(file_path))

    print(f"Loading retriever and LLM client...")
    retriever = Retriever()
    llm = GeminiClient()

    passed = 0
    failed = 0

    for case in cases:

        agent = SupportAgent(llm=llm, retriever=retriever)

        try:
            response, failures = run_case(agent, case)
        except Exception as e:
            failures = [f"exception during run: {e!r}"]
            response = None

        if failures:
            failed += 1
            print(f"\n[FAIL] {case['id']}")
            print(f"  response: {response!r}")
            for f in failures:
                print(f"  - {f}")
        else:
            passed += 1
            print(f"[PASS] {case['id']}")

    total = passed + failed
    print(f"\n{passed}/{total} cases passed.")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
