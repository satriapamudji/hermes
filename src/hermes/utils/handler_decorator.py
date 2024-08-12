from telethon import events

class HandlerCollector:
    def __init__(self):
        self.handlers = []
    def on(self, event_type):
        def decorator(func):
            self.handlers.append((event_type, func))
            return func
        return decorator

handler_collector = HandlerCollector()