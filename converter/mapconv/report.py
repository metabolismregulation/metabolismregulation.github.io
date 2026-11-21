import contextlib

KINDS = ('left out', 'changed', 'warning', 'summary', 'problem')
_messages = None


def say(kind, text):
    assert kind in KINDS, kind
    if _messages is None:
        print(text)
    else:
        _messages.append((kind, text))


@contextlib.contextmanager
def collect():
    global _messages
    outer, _messages = _messages, []
    try:
        yield _messages
    finally:
        _messages = outer
