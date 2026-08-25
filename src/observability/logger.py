import json
import sys
import time


class EventLogger:
    """
    Minimal structured event logger.

    Keeps the assignment's scope honest: no external logging
    infrastructure, just structured, greppable JSON lines that make it
    possible to audit routing decisions, tool calls, and safety
    interventions after the fact.
    """

    def __init__(self, stream=None):
        self.stream = stream or sys.stdout

    def log(self, event_type, **fields):

        record = {
            "timestamp": time.time(),
            "event": event_type,
            **fields
        }

        self.stream.write(json.dumps(record) + "\n")

        if hasattr(self.stream, "flush"):
            self.stream.flush()


default_logger = EventLogger()
