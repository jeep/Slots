from typing import Callable


class EntryField:
    def __init__(self, label: str, field_type: str, callback: Callable) -> None:
        self.label = label
        self.field_type = field_type
        self.callback = callback
