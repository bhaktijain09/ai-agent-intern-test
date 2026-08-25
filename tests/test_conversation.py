from src.conversation import Conversation


def test_starts_empty():

    conversation = Conversation()

    assert conversation.messages == []
    assert conversation.get_recent() == []


def test_add_user_and_assistant():

    conversation = Conversation()

    conversation.add_user("Hello")
    conversation.add_assistant("Hi there")

    assert conversation.messages == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]


def test_get_recent_limits_to_last_n():

    conversation = Conversation()

    for i in range(10):
        conversation.add_user(f"message {i}")

    recent = conversation.get_recent(limit=4)

    assert len(recent) == 4
    assert recent[-1]["content"] == "message 9"
    assert recent[0]["content"] == "message 6"


def test_get_recent_default_limit():

    conversation = Conversation()

    for i in range(10):
        conversation.add_user(f"message {i}")

    recent = conversation.get_recent()

    assert len(recent) == 6


def test_clear_resets_messages():

    conversation = Conversation()

    conversation.add_user("Hello")
    conversation.clear()

    assert conversation.messages == []
