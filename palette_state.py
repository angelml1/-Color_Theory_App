# where the current palette colors are kept
# history tracked for undo functionality
from dataclasses import dataclass, field

MAX_COLORS = 12


@dataclass
class Palette:
    colors: list[str] = field(default_factory=list)
    history: list[list[str]] = field(default_factory=list)
    _listeners: list = field(default_factory=list, repr=False)

    def subscribe(self, fn):
        self._listeners.append(fn)

    def _notify(self):
        for fn in self._listeners:
            fn()

    def set(self, colors):
        self.history = (self.history + [list(self.colors)])[-20:]
        self.colors = list(colors)[:MAX_COLORS]
        self._notify()

    def add(self, hex_color: str):
        if hex_color not in self.colors and len(self.colors) < MAX_COLORS:
            self.set(self.colors + [hex_color])

    def remove(self, hex_color: str):
        if hex_color in self.colors:
            self.set([c for c in self.colors if c != hex_color])

    def undo(self):
        if self.history:
            self.colors = self.history.pop()
            self._notify()