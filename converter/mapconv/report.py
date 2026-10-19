# The converter's messages, one list per conversion: each a kind and a text. Kinds: 'left out'
# (not converted, dropped), 'changed' (moved, joined, written another way), 'warning' (converted,
# worth a look), 'summary' (what a written file holds), 'problem' (a rule the map breaks,
# rules.py). Outside collect() a message is printed, as on the command line.
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
    # the messages said inside the block, in a list
    global _messages
    outer, _messages = _messages, []
    try:
        yield _messages
    finally:
        _messages = outer
