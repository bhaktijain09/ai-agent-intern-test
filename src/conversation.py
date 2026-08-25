class Conversation:

    def __init__(self):
        self.messages = []

    def add_user(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_assistant(self, message):
        self.messages.append({
            "role": "assistant",
            "content": message
        })

    def get_recent(self, limit=6):
        return self.messages[-limit:]

    def clear(self):
        self.messages = []
