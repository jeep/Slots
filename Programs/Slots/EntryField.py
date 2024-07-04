from typing import Callable


class EntryField:
    def __init__(self, label: str, field_type: str, val: str, callback: Callable = None) -> None:
        self.label = label
        self.field_type = field_type
        self.val = val
        self.callback = callback
