from typing import Callable


class EntryField:
    def __init__(self, label: str, callback: Callable) -> None:
        self.label = label
        self.callback = callback
